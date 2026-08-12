"""Translate text using DeepL with Playwright."""

import asyncio
import os
import re
import time
from collections.abc import Coroutine
from contextlib import suppress
from typing import Any, TypedDict

from install_playwright import install
from playwright._impl._errors import Error as PlaywrightError
from playwright.async_api import ProxySettings, async_playwright
from playwright.async_api._generated import Browser, Locator, Page, Playwright

from deepl.languages import AUTO_LANG, FR_LANGS, TO_LANGS

TRANSLATOR_URL = "https://www.deepl.com/en/translator"

# `auto` cannot be named in the URL fragment: DeepL drops a fragment it does not
# understand as a whole, taking the target language down with it, and falls back to
# translating into its own default. So an auto source is arranged by pinning some other
# language and leaving the detection to do what it does to any pinned source anyway —
# replace it with the language the text is actually in, keeping the target as asked.
# The stand-in only has to differ from the target, since the text decides the outcome;
# pinning the target as the source would make DeepL swap the pair instead.
_AUTO_PLACEHOLDER_LANGS = ("en", "de")

# DeepL renders the translator as a client-side app; these are the stable hooks it exposes.
_SOURCE_INPUT = "[data-testid=translator-source-input]"
_TARGET_INPUT = "[data-testid=translator-target-input]"
_SOURCE_TEXTBOX = f"{_SOURCE_INPUT} div[role=textbox]"
_TARGET_OUTPUT = "d-textarea[aria-labelledby=translation-target-heading]"
# The editor inside the output widget, which holds the text even when the widget's own
# `value` accessor is unavailable.
_TARGET_EDITOR = "[contenteditable], div[role=textbox]"

# DeepL's "Checking if the connection is secure..." overlay. Once this covers the
# translator, the page is frozen behind it: whatever has been translated already is all
# that is going to arrive.
_CHALLENGE_WIDGET = "#challenge-widget"

# The cookie consent dialog, which sits in front of the translator until it is
# answered. Its markup lives in a shadow root, which Playwright selectors reach into
# but `document.querySelector` does not.
_CONSENT_BUTTON = "#uc-cmp-footer button[data-action-type=accept]"
# How long to give the dialog to disappear once accepted.
_CONSENT_TIMEOUT_MS = 3000
# The consent script starts up *after* the translator input appears, so a dialog that
# is coming may not be there yet when the input is first usable. Rather than idle until
# it might show — which is exactly what costs the run its chance to type — the text is
# entered right away, and the dialog is only waited for if it turns out to have been in
# the way. Text already in the input keeps translating with a dialog over the page, so
# one that arrives late does not matter.
_CONSENT_WAIT_MS = 2500
_CONSENT_POLL_MS = 100

# Placeholder DeepL shows in the output while a sentence is still being translated.
_PENDING_MARKER = "[...]"

# The output is streamed, so it is only trusted once it stops changing for this long.
_POLL_INTERVAL_MS = 500

_EXCLUDED_RESOURCES = frozenset({"image", "media", "font", "other"})

# Filling the input straight from JS looks nothing like a person using the page, and
# Cloudflare answers that with a captcha. Instead the pointer travels to the input,
# clicks it, and the text arrives as a paste — the same events a human would produce.
_MOUSE_MOVE_STEPS = 24
_BEFORE_CLICK_MS = 250
_CLICK_PRESS_MS = 60
_AFTER_CLICK_MS = 200
_PASTE_SHORTCUT = "ControlOrMeta+V"
_SELECT_ALL_SHORTCUT = "ControlOrMeta+A"
_CLIPBOARD_PERMISSIONS = ["clipboard-read", "clipboard-write"]

# Aim a little above and left of the middle, where a person tends to land, rather
# than dead centre.
_CLICK_X_RATIO = 0.3
_CLICK_Y_RATIO = 0.25

# The editor renders pasted text asynchronously, so give it a moment to show up.
_INPUT_CHECK_ATTEMPTS = 6
_INPUT_CHECK_INTERVAL_MS = 250

_WHITESPACE = re.compile(r"\s+")

_WRITE_CLIPBOARD_JS = "(text) => navigator.clipboard.writeText(text)"
# Resolves to null instead of rejecting when the clipboard holds something unreadable.
_READ_CLIPBOARD_JS = "() => navigator.clipboard.readText().catch(() => null)"

_IS_INPUT_FOCUSED_JS = f"""
    () => {{
        const textbox = document.querySelector("{_SOURCE_TEXTBOX}");
        return textbox !== null && textbox.contains(document.activeElement);
    }}
"""

_READ_STATE_JS = f"""
    () => {{
        const source = document.querySelector("{_SOURCE_INPUT}");
        const target = document.querySelector("{_TARGET_INPUT}");
        const output = document.querySelector("{_TARGET_OUTPUT}");
        let text = output && typeof output.value === "string" ? output.value : null;
        if (output && !(text && text.trim())) {{
            // The widget stops answering for its value once the connection check
            // covers the page, but the translation is still in the editor below it.
            // An empty editor reads as a bare line break, which is not a translation.
            const editor = output.querySelector("{_TARGET_EDITOR}");
            const fallback = editor ? editor.innerText.trim() : "";
            if (fallback) {{
                text = fallback;
            }}
        }}
        return {{
            fr_lang: source ? source.getAttribute("lang") : null,
            to_lang: target ? target.getAttribute("lang") : null,
            text: text,
            challenged: document.querySelector("{_CHALLENGE_WIDGET}") !== null,
        }};
    }}
"""


class _PageState(TypedDict):
    """Snapshot of the translator widget."""

    fr_lang: str | None
    to_lang: str | None
    text: str | None
    challenged: bool


class DeepLCLIError(Exception):
    """Generic error for DeepLCLI."""


class DeepLCLIPageLoadError(Exception):
    """Page load error for DeepLCLI."""


class DeepLCLI:
    """Translate text using DeepL with Playwright."""

    def __init__(
        self,
        fr_lang: str,
        to_lang: str,
        timeout: int = 15000,
        proxy: ProxySettings | None = None,
        *,
        headless: bool = True,
    ) -> None:
        """Initialize DeepLCLI.

        Args:
            fr_lang (str): Source language, or `auto` to let DeepL detect it. The
                detected language is reported in `translated_fr_lang` afterwards.
            to_lang (str): Target language.
            timeout (int): Timeout in milliseconds. Default is 15000ms.
            proxy (ProxySettings): Use a proxy to access deepl.
            headless (bool): Run the browser headless. Set to False to watch the
                translator page in a real browser window. Default is True.

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
        self.headless = headless

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
        if self.headless:
            # Skip what is only needed for a human to look at the page.
            await page.route(
                "**/*",
                lambda route: (
                    route.abort() if route.request.resource_type in _EXCLUDED_RESOURCES else route.continue_()
                ),
            )

        url = f"{TRANSLATOR_URL}#{self.__fragment_fr_lang()}/{self.to_lang}/"

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

        await self.__wait_for_translator(page)

        return page

    async def __wait_for_translator(self, page: Page) -> None:
        """Wait for the source input, answering the cookie dialog if one shows up.

        The dialog is looked for while the app is still loading, which costs nothing.
        One that has not appeared by the time the input has is left to
        __wait_for_translation, rather than waited for here at the expense of typing.

        Args:
            page (Page): Translator page.

        Raises:
            DeepLCLIPageLoadError: If the translator does not become usable in time.
        """
        textbox = page.locator(_SOURCE_TEXTBOX)
        deadline = time.monotonic() + self.timeout / 1000

        while not await textbox.is_visible():
            if time.monotonic() > deadline:
                msg = f"Maybe Time limit exceeded. ({self.timeout} ms)"
                raise DeepLCLIPageLoadError(msg)

            await self.__accept_cookies(page)
            await page.wait_for_timeout(_CONSENT_POLL_MS)

        # One last look before handing over to the typing, which happens immediately.
        await self.__accept_cookies(page)

    async def __accept_cookies(self, page: Page, *, wait: bool = False) -> bool:
        """Answer the cookie consent dialog if DeepL is showing one.

        The dialog is laid over the translator, so the source input cannot be
        clicked until it is gone.

        Args:
            page (Page): Translator page.
            wait (bool): Give a dialog time to appear rather than only taking the one
                that is already there. Only worth doing once something has gone wrong,
                since idling in front of the translator is what breaks it.

        Returns:
            bool: Whether a dialog was there and got accepted.

        Raises:
            DeepLCLIPageLoadError: If the dialog is shown but does not go away.
        """
        button = page.locator(_CONSENT_BUTTON).first

        if wait:
            try:
                await button.wait_for(state="visible", timeout=_CONSENT_WAIT_MS)
            except PlaywrightError:
                return False
        elif not await button.count() or not await button.is_visible():
            return False

        try:
            await self.__click(page, button)
            await button.wait_for(state="hidden", timeout=_CONSENT_TIMEOUT_MS)
        except PlaywrightError as e:
            msg = "The cookie consent dialog did not close"
            raise DeepLCLIPageLoadError(msg) from e

        return True

    async def __input_script(self, page: Page, script: str) -> None:
        """Put the source text into the translator input the way a person would.

        The pointer is moved onto the input and clicks it, then the text is pasted
        from the clipboard. Setting the value directly is what makes Cloudflare ask
        for a captcha, so it is only kept as a last resort if the paste is refused
        (the clipboard is unavailable in some sandboxes).

        This runs as soon as the input appears, and deliberately does not wait around
        beforehand: a few seconds after load, DeepL stops letting the input take focus
        at all, and nothing can be entered for the rest of the visit.

        Args:
            page (Page): Translator page.
            script (str): Text to translate.

        Raises:
            DeepLCLIPageLoadError: If the text cannot be entered.
        """
        textbox = page.locator(_SOURCE_TEXTBOX)
        try:
            entered = await self.__click_and_paste(page, textbox, script)

            if not entered and await self.__accept_cookies(page, wait=True):
                # A cookie dialog was over the input and took the click; now it is
                # gone, the same approach can be tried again.
                entered = await self.__click_and_paste(page, textbox, script)

            if not entered:
                await self.__retype_script(page, textbox, script)
                entered = await self.__wait_for_script(textbox, page, script)
        except PlaywrightError as e:
            msg = "Unable to enter the source text"
            raise DeepLCLIPageLoadError(msg) from e

        if not entered:
            # Reported here rather than left to time out as a translation that never
            # arrives, which says nothing about the input being the problem.
            msg = "The source text did not reach the translator input"
            raise DeepLCLIPageLoadError(msg)

    async def __click_and_paste(self, page: Page, textbox: Locator, script: str) -> bool:
        """Click the input, paste the text, and report whether it arrived.

        Args:
            page (Page): Translator page.
            textbox (Locator): The source input.
            script (str): Text to translate.

        Returns:
            bool: Whether the text is in the input.
        """
        await self.__click_input(page, textbox)
        await self.__paste_script(page, script)

        return await self.__wait_for_script(textbox, page, script)

    async def __click_input(self, page: Page, textbox: Locator) -> None:
        """Click the source input, making sure it ends up focused.

        Args:
            page (Page): Translator page.
            textbox (Locator): The source input.
        """
        await self.__click(page, textbox)

        if not await page.evaluate(_IS_INPUT_FOCUSED_JS):
            # Something on top of the card swallowed the click.
            await textbox.focus()

    @staticmethod
    async def __click(page: Page, target: Locator) -> None:
        """Move the pointer onto an element and click it, the way a person would.

        Args:
            page (Page): Translator page.
            target (Locator): Element to click.
        """
        # Not scrolled into view first: the translator card and the consent dialog are
        # both within the viewport already, and that call is one DeepL can leave hanging.
        box = await target.bounding_box()

        if box is None:
            # No geometry to aim at, so let Playwright place the click itself.
            await target.click(delay=_CLICK_PRESS_MS)
        else:
            x = box["x"] + box["width"] * _CLICK_X_RATIO
            y = box["y"] + box["height"] * _CLICK_Y_RATIO
            # A real pointer travels to its target instead of teleporting.
            await page.mouse.move(x, y, steps=_MOUSE_MOVE_STEPS)
            await page.wait_for_timeout(_BEFORE_CLICK_MS)
            await page.mouse.click(x, y, delay=_CLICK_PRESS_MS)

        await page.wait_for_timeout(_AFTER_CLICK_MS)

    async def __paste_script(self, page: Page, script: str) -> None:
        """Paste the text into the focused input via the clipboard.

        A headed browser shares the clipboard with the rest of the desktop, so
        whatever the user had on it is read first and put back afterwards.

        Args:
            page (Page): Translator page.
            script (str): Text to translate.
        """
        try:
            await page.context.grant_permissions(_CLIPBOARD_PERMISSIONS)
            clipboard: str | None = await page.evaluate(_READ_CLIPBOARD_JS)
            await page.evaluate(_WRITE_CLIPBOARD_JS, script)
        except PlaywrightError:
            # No clipboard access; __input_script falls back to typing the text.
            return

        try:
            await page.keyboard.press(_PASTE_SHORTCUT)
            await page.wait_for_timeout(_AFTER_CLICK_MS)
        finally:
            await self.__restore_clipboard(page, clipboard)

    @staticmethod
    async def __restore_clipboard(page: Page, clipboard: str | None) -> None:
        """Put the user's own clipboard contents back.

        Only text can be restored: anything else was already unreadable, and is
        left replaced by the source text.

        Args:
            page (Page): Translator page.
            clipboard (str | None): What the clipboard held before pasting.
        """
        if not clipboard:
            return

        # Losing the clipboard is not worth failing a translation over.
        with suppress(PlaywrightError):
            await page.evaluate(_WRITE_CLIPBOARD_JS, clipboard)

    @staticmethod
    async def __wait_for_script(textbox: Locator, page: Page, script: str) -> bool:
        """Wait for the input to hold the text, ignoring how it wraps lines.

        The editor renders what it is given a moment later, so a single check right
        after the paste can miss text that did arrive.

        Args:
            textbox (Locator): The source input.
            page (Page): Translator page.
            script (str): Text that should be in the input.

        Returns:
            bool: Whether the text is in the input.
        """
        wanted = _WHITESPACE.sub(" ", script).strip()

        for _ in range(_INPUT_CHECK_ATTEMPTS):
            entered = await textbox.inner_text()
            if _WHITESPACE.sub(" ", entered).strip() == wanted:
                return True
            await page.wait_for_timeout(_INPUT_CHECK_INTERVAL_MS)

        return False

    @staticmethod
    async def __retype_script(page: Page, textbox: Locator, script: str) -> None:
        """Replace whatever the paste left behind with the text itself.

        `insert_text` reaches the page as one `insertText` event, the same way text
        committed from an IME does, so it does not look like a filled-in form either.

        Args:
            page (Page): Translator page.
            textbox (Locator): The source input.
            script (str): Text to translate.
        """
        await textbox.focus()
        # A partial paste would otherwise be left in front of the text.
        await page.keyboard.press(_SELECT_ALL_SHORTCUT)
        await page.keyboard.press("Delete")
        await page.keyboard.insert_text(script)

    async def __wait_for_translation(self, page: Page) -> _PageState:
        """Wait until the translation is complete and stable.

        DeepL streams the output sentence by sentence, so a non-empty output is not
        necessarily the final one. Poll until the same output is seen twice in a row.

        A cookie dialog is answered here if one turns up, which is where it usually
        does: the consent script starts up later than the translator. Doing it during
        a wait that was happening anyway keeps it off the critical path, and text
        already in the input goes on being translated meanwhile.

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
        dialog_pending = True

        while time.monotonic() < deadline:
            if dialog_pending:
                try:
                    dialog_pending = not await self.__accept_cookies(page)
                except DeepLCLIPageLoadError:
                    # A dialog that will not close is no reason to throw away a
                    # translation that is arriving regardless, so it is left alone.
                    dialog_pending = False

            if self.__has_output(state):
                settled = previous is not None and previous["text"] == state["text"]

                # A challenged page will never get as far as the requested pair, so the
                # translation on screen is taken as final rather than waited out.
                if settled and (self.__is_translated(state) or state["challenged"]):
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

    def __fragment_fr_lang(self) -> str:
        """Pick the source language to put in the URL fragment.

        Returns:
            str: The requested source language, or a stand-in for it when DeepL is
                the one detecting it.
        """
        if self.fr_lang != AUTO_LANG:
            return self.fr_lang

        target = self.to_lang.split("-")[0].lower()

        return next(lang for lang in _AUTO_PLACEHOLDER_LANGS if lang != target)

    def __is_translated(self, state: _PageState) -> bool:
        """Check whether the state holds a complete translation of the requested pair."""
        return (
            self.__fr_lang_applied(state["fr_lang"])
            and self.__lang_applied(state["to_lang"], self.to_lang)
            and self.__has_output(state)
        )

    def __fr_lang_applied(self, actual: str | None) -> bool:
        """Check whether DeepL is translating from the requested source language.

        Args:
            actual (str | None): The language DeepL is translating from.

        Returns:
            bool: Whether that is the source language that was asked for.
        """
        if self.fr_lang == AUTO_LANG:
            # DeepL reports the language it detected and never `auto` itself, so
            # whatever it settled on is the language that was asked for.
            return actual is not None

        return self.__lang_applied(actual, self.fr_lang)

    @staticmethod
    def __has_output(state: _PageState) -> bool:
        """Check whether the output holds a translation that is no longer mid-sentence."""
        text = state["text"]

        # An input the user cannot see anything in must not read as a finished result,
        # so whitespace on its own does not count as output.
        return bool(text) and bool(text.strip()) and _PENDING_MARKER not in text

    @staticmethod
    def __lang_applied(actual: str | None, expected: str) -> bool:
        """Check whether DeepL selected the expected language (it reports e.g. `en-US`)."""
        return actual is not None and actual.lower() == expected.lower()

    def __describe_timeout(self, state: _PageState) -> str:
        """Explain why waiting for the translation timed out."""
        if state["challenged"]:
            return (
                "DeepL is checking whether the connection is secure and nothing was "
                f"translated behind that check. ({self.timeout} ms)"
            )

        if not self.__fr_lang_applied(state["fr_lang"]) or not self.__lang_applied(
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

        args = [
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--window-size=1920,1080",
        ]
        if self.headless:
            # These make the headless browser cheaper to start, but a headed
            # Chromium does not survive them.
            args += ["--disable-gpu", "--no-zygote"]
            if os.name != "nt":
                args.append("--single-process")

        return await p.chromium.launch(
            headless=self.headless,
            args=args,
            proxy=self.proxy,
        )
