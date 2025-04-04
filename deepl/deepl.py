"""Translate text using DeepL with Playwright."""

import asyncio
import contextlib
import os
from collections.abc import Coroutine
from functools import partial
from typing import Any, ClassVar
from urllib.parse import quote

from install_playwright import install
from playwright._impl._errors import Error as PlaywrightError
from playwright.async_api import async_playwright
from playwright.async_api._generated import Browser, Playwright


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
    // cost to =
    Array.from(
        document.querySelectorAll(`button[data-testid^='translator-lang-option']`)
    ).map(e=>e.getAttribute('data-testid').split('translator-lang-option-')[1].toLowerCase())
    // new Set(fr).difference(new Set(to))
    // new Set(to).difference(new Set(fr))
    ```
    """

    fr_langs: ClassVar[set[str]] = {
        # "auto",
        "ar",
        "bg",
        "zh",
        "cs",
        "da",
        "nl",
        "en",
        "et",
        "fi",
        "fr",
        "de",
        "el",
        "hu",
        "id",
        "it",
        "ja",
        "ko",
        "lv",
        "lt",
        "nb",
        "pl",
        "pt",
        "ro",
        "ru",
        "sk",
        "sl",
        "es",
        "sv",
        "tr",
        "uk",
    }
    to_langs = fr_langs | {"zh-hans", "zh-hant", "en-us", "en-gb", "pt-pt", "pt-br"} - {
        "auto",
        "zh",
        "en",
        "pt",
    }

    def __init__(
        self,
        fr_lang: str,
        to_lang: str,
        timeout: int = 15000,
        *,
        use_dom_submit: bool = False,
    ) -> None:
        """Initialize DeepLCLI.

        Args:
            fr_lang (str): Source language.
            to_lang (str): Target language.
            timeout (int): Timeout in milliseconds. Default is 15000ms.
            use_dom_submit (bool): Use DOM submit instead of URL. Default is False.

        Raises:
            DeepLCLIError: If the language is not valid.
        """
        if fr_lang not in self.fr_langs:
            raise DeepLCLIError(
                f"{fr_lang!r} is not valid language. Valid language:\n" + repr(self.fr_langs),
            )
        if to_lang not in self.to_langs:
            raise DeepLCLIError(
                f"{to_lang!r} is not valid language. Valid language:\n" + repr(self.to_langs),
            )

        self.fr_lang = fr_lang
        self.to_lang = to_lang
        self.translated_fr_lang: str | None = None
        self.translated_to_lang: str | None = None
        self.max_length = 1500
        self.timeout = timeout
        self.use_dom_submit = use_dom_submit

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

        # run in the current thread
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.__translate(script))

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

    async def __translate(self, script: str) -> str:  # noqa: C901, PLR0915
        """Throw a request."""
        async with async_playwright() as p:
            # Dry run
            try:
                browser = await self.__get_browser(p)
            except PlaywrightError as e:
                if "playwright install" in e.message:
                    await asyncio.get_event_loop().run_in_executor(
                        None,
                        partial(install, p.chromium, with_deps=True),
                    )
                    await asyncio.get_event_loop().run_in_executor(
                        None,
                        install,
                        p.chromium,
                    )
                    browser = await self.__get_browser(p)
                else:
                    raise

            page = await browser.new_page()
            page.set_default_timeout(self.timeout)

            # skip loading page resources for improving performance
            excluded_resources = ["image", "media", "font", "other"]
            await page.route(
                "**/*",
                lambda route: (
                    route.abort() if route.request.resource_type in excluded_resources else route.continue_()
                ),
            )

            url = "https://www.deepl.com/en/translator"
            if self.use_dom_submit:
                await page.goto(url)
            else:
                script = quote(script, safe="")
                await page.goto(f"{url}#{self.fr_lang}/{self.to_lang}/{script}")

            # Wait for loading to complete
            try:
                page.get_by_role("main")
            except PlaywrightError as e:
                msg = f"Maybe Time limit exceeded. ({self.timeout} ms)"
                raise DeepLCLIPageLoadError(msg) from e

            if self.use_dom_submit:
                # banner prevents clicking on language buttons, close the banner first
                await page.click("button[data-testid=cookie-banner-lax-close-button]")
                # we also expect the Chrome extension banner to show up
                with contextlib.suppress(PlaywrightError):
                    await page.wait_for_function(
                        """
                        () => document.querySelector('div[data-testid="chrome-extension-toast"]')
                        """,
                    )

                # try to close the extension banner
                with contextlib.suppress(PlaywrightError):
                    await page.evaluate(
                        """
                        document.querySelector(
                            'div[data-testid="chrome-extension-toast"]',
                        ).querySelector('button').click()
                        """,
                    )

                # select input / output language
                await page.locator(
                    "button[data-testid=translator-source-lang-btn]",
                ).dispatch_event("click")
                await (
                    page.get_by_test_id("translator-source-lang-list")
                    .get_by_test_id(
                        f"translator-lang-option-{self.fr_lang}",
                    )
                    .dispatch_event("click")
                )
                await page.locator(
                    "button[data-testid=translator-target-lang-btn]",
                ).dispatch_event("click")
                await (
                    page.get_by_test_id("translator-target-lang-list")
                    .get_by_test_id(
                        f"translator-lang-option-{self.to_lang}",
                    )
                    .dispatch_event("click")
                )
                # fill in the form of translating script
                await page.fill(
                    "div[aria-labelledby=translation-source-heading]",
                    script,
                )

            # Wait for translation to complete (perhaps partially)
            try:
                await page.wait_for_function(
                    """
                    () => document.querySelector(
                    'd-textarea[aria-labelledby=translation-target-heading]')?.value?.length > 0
                    """,
                )
            except PlaywrightError as e:
                msg = f"Time limit exceeded. ({self.timeout} ms)"
                raise DeepLCLIPageLoadError(msg) from e

            # Get the number of lines in the translated text field
            try:
                line_count = await page.evaluate(
                    """
                    document.querySelector(
                        'd-textarea[aria-labelledby=translation-target-heading]',
                    ).children[0].children.length
                    """,
                )
            except PlaywrightError as e:
                msg = "Unable to evaluate line count of the translation"
                raise DeepLCLIPageLoadError(msg) from e

            # Since the site may not output all lines at once, we wait until each line is finished
            # and then add it to the list of translated lines
            translated_lines = []
            for line_index in range(line_count):
                try:
                    await page.wait_for_function(
                        f"""
                        () => {{
                            t = document.querySelector(
                                'd-textarea[aria-labelledby=translation-target-heading]',
                            )?.children[0]?.children[{line_index}]?.innerText ?? '';
                            return t.length > 0 && !t.includes('[...]');
                        }}
                        """,
                    )
                except PlaywrightError as e:
                    msg = f"Time limit exceeded for line {line_index}. ({self.timeout} ms)"
                    raise DeepLCLIPageLoadError(msg) from e

                try:
                    translated_text = await page.evaluate(
                        f"""
                        document.querySelector(
                            'd-textarea[aria-labelledby=translation-target-heading]'
                        ).children[0].children[{line_index}].innerText
                        """,
                    )
                    translated_lines.append(translated_text)
                except PlaywrightError as e:
                    msg = f"Unable get translated text for line {line_index}"
                    raise DeepLCLIPageLoadError(msg) from e

            # Get information
            input_textbox = page.get_by_role("region", name="Source text").locator(
                "d-textarea",
            )
            output_textbox = page.get_by_role(
                "region",
                name="Translation results",
            ).locator("d-textarea")

            self.translated_fr_lang = str(
                await input_textbox.get_attribute("lang"),
            ).split("-")[0]
            self.translated_to_lang = str(
                await output_textbox.get_attribute("lang"),
            ).split("-")[0]

            res = "".join(translated_lines)

            await browser.close()

            return res

    def __sanitize_script(self, script: str) -> str:
        """Check command line args and stdin."""
        script = script.rstrip("\n")

        if self.max_length is not None and len(script) > self.max_length:
            msg = f"Limit of script is less than {self.max_length} chars (Now: {len(script)} chars)"
            raise DeepLCLIError(msg)

        if len(script) <= 0:
            msg = "Script seems to be empty."
            raise DeepLCLIError(msg)

        return script.replace("/", r"\/").replace("|", r"\|")

    async def __get_browser(self, p: Playwright) -> Browser:
        """Launch browser executable and get playwright browser object."""
        return await p.chromium.launch(
            headless=True,  # for debug, change into `False`
            args=[
                "--no-sandbox",
                "--single-process" if os.name != "nt" else "",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--no-zygote",
                "--window-size=1920,1080",
            ],
        )
