"""Translate text using DeepL with Playwright."""

import asyncio
import os
import time
from collections.abc import Coroutine
from typing import Any, TypedDict

from install_playwright import install
from playwright._impl._errors import Error as PlaywrightError
from playwright.async_api import ProxySettings, async_playwright
from playwright.async_api._generated import Browser, Page, Playwright

from deepl.languages import FR_LANGS, TO_LANGS

TRANSLATOR_URL = "https://www.deepl.com/en/translator"

# DeepL renders the translator as a client-side app; these are the stable hooks it exposes.
_SOURCE_INPUT = "[data-testid=translator-source-input]"
_TARGET_INPUT = "[data-testid=translator-target-input]"
_SOURCE_TEXTBOX = f"{_SOURCE_INPUT} div[role=textbox]"
_TARGET_OUTPUT = "d-textarea[aria-labelledby=translation-target-heading]"

# Placeholder DeepL shows in the output while a sentence is still being translated.
_PENDING_MARKER = "[...]"

# The output is streamed, so it is only trusted once it stops changing for this long.
_POLL_INTERVAL_MS = 500

_EXCLUDED_RESOURCES = frozenset({"image", "media", "font", "other"})

_READ_STATE_JS = f"""
    () => {{
        const source = document.querySelector("{_SOURCE_INPUT}");
        const target = document.querySelector("{_TARGET_INPUT}");
        const output = document.querySelector("{_TARGET_OUTPUT}");
        return {{
            fr_lang: source ? source.getAttribute("lang") : null,
            to_lang: target ? target.getAttribute("lang") : null,
            text: output ? output.value : null,
        }};
    }}
"""


class _PageState(TypedDict):
    """Snapshot of the translator widget."""

    fr_lang: str | None
    to_lang: str | None
    text: str | None


class DeepLCLIError(Exception):
    """Generic error for DeepLCLI."""


class DeepLCLIPageLoadError(Exception):
    """Page load error for DeepLCLI."""


class DeepLCLI:
    """Translate text using DeepL with Playwright.

    How to get language list:

    1. open language dropdown
    2. run on console:

    ```
    // const fr =
    // const to =
    Array.from(
        document.querySelectorAll(`[data-testid^='translator-lang-option']`)
    ).map(e=>e.getAttribute('data-testid').replace(/^translator-lang-option-/, ''))
     .filter(e=>!e.endsWith('-pin'))
    // new Set(fr).difference(new Set(to))
    // new Set(to).difference(new Set(fr))
    ```
    """

    def __init__(
        self,
        fr_lang: str,
        to_lang: str,
        timeout: int = 15000,
        proxy: ProxySettings | None = None,
    ) -> None:
        """Initialize DeepLCLI.

        Args:
            fr_lang (str): Source language.
            to_lang (str): Target language.
            timeout (int): Timeout in milliseconds. Default is 15000ms.
            proxy (ProxySettings): Use a proxy to access deepl.

        Raises:
            DeepLCLIError: If the language is not valid.
        """
        if fr_lang not in FR_LANGS:
            raise DeepLCLIError(
                f"{fr_lang!r} is not valid language. Valid language:\n" + repr(FR_LANGS),
            )
        if to_lang not in TO_LANGS:
            raise DeepLCLIError(
                f"{to_lang!r} is not valid language. Valid language:\n" + repr(TO_LANGS),
            )

        self.fr_lang = fr_lang
        self.to_lang = to_lang
        self.translated_fr_lang: str | None = None
        self.translated_to_lang: str | None = None
        self.max_length = 1500
        self.timeout = timeout
        self.proxy = proxy

    def translate(self, script: str) -> str:
        """Translate script.

        Args:
            script (str): Script to translate.

        Returns:
            str: Translated script.

        Raises:
            DeepLCLIError: If the script is empty or too long.
            DeepLCLIPageLoadError: If the page load fails.
        """
        script = self.__sanitize_script(script)

        return asyncio.run(self.__translate(script))

    def translate_async(self, script: str) -> Coroutine[Any, Any, str]:
        """Translate script asynchronously.

        Args:
            script (str): Script to translate.

        Returns:
            Coroutine[Any, Any, str]: Translated script.

        Raises:
            DeepLCLIError: If the script is empty or too long.
            DeepLCLIPageLoadError: If the page load fails.
        """
        script = self.__sanitize_script(script)

        return self.__translate(script)

    async def __translate(self, script: str) -> str:
        """Throw a request."""
        async with async_playwright() as p:
            browser = await self.__get_browser(p)
            try:
                page = await self.__open_translator(browser)
                await self.__input_script(page, script)
                state = await self.__wait_for_translation(page)
            finally:
                await browser.close()

        self.translated_fr_lang = str(state["fr_lang"]).split("-")[0]
        self.translated_to_lang = str(state["to_lang"]).split("-")[0]

        return str(state["text"])

    async def __open_translator(self, browser: Browser) -> Page:
        """Open the translator page with the requested language pair selected.

        The language pair is passed through the URL fragment, which DeepL applies on load.
        That avoids driving the language dropdowns, which are covered by an anti-bot
        overlay and only respond once the client-side app has hydrated.

        Args:
            browser (Browser): Browser to open the page in.

        Returns:
            Page: The loaded translator page.

        Raises:
            DeepLCLIError: If the page responds with an error status.
            DeepLCLIPageLoadError: If the translator does not become usable in time.
        """
        page = await browser.new_page()
        page.set_default_timeout(self.timeout)
        await page.set_viewport_size({"width": 1920, "height": 1080})
        await page.route(
            "**/*",
            lambda route: route.abort() if route.request.resource_type in _EXCLUDED_RESOURCES else route.continue_(),
        )

        url = f"{TRANSLATOR_URL}#{self.fr_lang}/{self.to_lang}/"

        def is_document_response(resp: Any) -> bool:  # noqa: ANN401
            # The fragment is never sent to the server, so it is absent from the response URL.
            return resp.url.split("#")[0] == TRANSLATOR_URL and resp.request.method == "GET"

        async with page.expect_response(is_document_response) as resp_info:
            await page.goto(url)

        response = await resp_info.value

        if not response.ok:
            error_text = await page.inner_text("body > main > div > p")

            msg = f"Page loading failed with status code {response.status}: {error_text}"
            raise DeepLCLIError(msg)

        try:
            await page.wait_for_selector(_SOURCE_TEXTBOX, state="visible")
        except PlaywrightError as e:
            msg = f"Maybe Time limit exceeded. ({self.timeout} ms)"
            raise DeepLCLIPageLoadError(msg) from e

        return page

    async def __input_script(self, page: Page, script: str) -> None:
        """Put the source text into the translator input.

        Args:
            page (Page): Translator page.
            script (str): Text to translate.

        Raises:
            DeepLCLIPageLoadError: If the text cannot be entered.
        """
        try:
            await page.fill(_SOURCE_TEXTBOX, script)
        except PlaywrightError as e:
            msg = "Unable to enter the source text"
            raise DeepLCLIPageLoadError(msg) from e

    async def __wait_for_translation(self, page: Page) -> _PageState:
        """Wait until the translation is complete and stable.

        DeepL streams the output sentence by sentence, so a non-empty output is not
        necessarily the final one. Poll until the same output is seen twice in a row.

        Args:
            page (Page): Translator page.

        Returns:
            _PageState: The settled state of the translator widget.

        Raises:
            DeepLCLIPageLoadError: If the translation does not settle in time.
        """
        deadline = time.monotonic() + self.timeout / 1000
        state = await self.__read_state(page)
        previous: _PageState | None = None

        while time.monotonic() < deadline:
            if self.__is_translated(state):
                if previous is not None and previous["text"] == state["text"]:
                    return state
                previous = state
            else:
                previous = None

            await page.wait_for_timeout(_POLL_INTERVAL_MS)
            state = await self.__read_state(page)

        raise DeepLCLIPageLoadError(self.__describe_timeout(state))

    async def __read_state(self, page: Page) -> _PageState:
        """Read the current languages and output text from the translator widget."""
        try:
            state: _PageState = await page.evaluate(_READ_STATE_JS)
        except PlaywrightError as e:
            msg = "Unable to read the translator state"
            raise DeepLCLIPageLoadError(msg) from e

        return state

    def __is_translated(self, state: _PageState) -> bool:
        """Check whether the state holds a complete translation of the requested pair."""
        text = state["text"]

        return (
            self.__lang_applied(state["fr_lang"], self.fr_lang)
            and self.__lang_applied(state["to_lang"], self.to_lang)
            and bool(text)
            and _PENDING_MARKER not in str(text)
        )

    @staticmethod
    def __lang_applied(actual: str | None, expected: str) -> bool:
        """Check whether DeepL selected the expected language (it reports e.g. `en-US`)."""
        return actual is not None and actual.lower() == expected.lower()

    def __describe_timeout(self, state: _PageState) -> str:
        """Explain why waiting for the translation timed out."""
        if not self.__lang_applied(state["fr_lang"], self.fr_lang) or not self.__lang_applied(
            state["to_lang"],
            self.to_lang,
        ):
            return (
                f"DeepL did not select the requested language pair "
                f"(wanted {self.fr_lang!r} -> {self.to_lang!r}, "
                f"got {state['fr_lang']!r} -> {state['to_lang']!r}). ({self.timeout} ms)"
            )

        return f"Time limit exceeded. ({self.timeout} ms)"

    def __sanitize_script(self, script: str) -> str:
        """Check command line args and stdin."""
        script = script.rstrip("\n")

        if self.max_length is not None and len(script) > self.max_length:
            msg = f"Limit of script is less than {self.max_length} chars (Now: {len(script)} chars)"
            raise DeepLCLIError(msg)

        if len(script) <= 0:
            msg = "Script seems to be empty."
            raise DeepLCLIError(msg)

        return script

    async def __get_browser(self, p: Playwright) -> Browser:
        """Launch browser executable and get playwright browser object."""
        install([p.chromium], with_deps=True)

        return await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--single-process" if os.name != "nt" else "",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--no-zygote",
                "--window-size=1920,1080",
            ],
            proxy=self.proxy,
        )
