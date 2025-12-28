"""Translate text using DeepL with Playwright."""

import asyncio
import contextlib
import os
from collections.abc import Coroutine
from typing import Any

from install_playwright import install
from playwright._impl._errors import Error as PlaywrightError
from playwright.async_api import async_playwright
from playwright.async_api._generated import Browser, Playwright

from deepl.languages import FR_LANGS, TO_LANGS


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

    def __init__(
        self,
        fr_lang: str,
        to_lang: str,
        timeout: int = 15000,
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

            page = await browser.new_page()
            page.set_default_timeout(self.timeout)
            await page.set_viewport_size({"width": 1920, "height": 1080})
            excluded_resources = ["image", "media", "font", "other"]
            await page.route(
                "**/*",
                lambda route: (
                    route.abort() if route.request.resource_type in excluded_resources else route.continue_()
                ),
            )

            url = "https://www.deepl.com/en/translator"
            await page.goto(url)

            try:
                page.get_by_role("main")
            except PlaywrightError as e:
                msg = f"Maybe Time limit exceeded. ({self.timeout} ms)"
                raise DeepLCLIPageLoadError(msg) from e

            with contextlib.suppress(PlaywrightError):
                await page.click("button[id=cookie-banner-lax-close-button]")
                await page.wait_for_function(
                    """
                    () => document.querySelector('div[data-testid="chrome-extension-toast"]')
                    """,
                )
                await page.evaluate(
                    """
                    document.querySelector(
                        'div[data-testid="chrome-extension-toast"]',
                    ).querySelector('button').click()
                    """,
                )

            await page.locator(
                "button[data-testid=translator-source-lang-btn]",
            ).dispatch_event("click")

            await (
                page.get_by_test_id("translator-source-lang-list")
                .get_by_test_id(
                    f"translator-lang-option-{self.fr_lang}",
                )
                .first.dispatch_event("click")
            )

            await page.locator(
                "button[data-testid=translator-target-lang-btn]",
            ).dispatch_event("click")

            await (
                page.get_by_test_id("translator-target-lang-list")
                .get_by_test_id(
                    f"translator-lang-option-{self.to_lang}",
                )
                .first.dispatch_event("click")
            )

            await page.fill(
                "div[aria-labelledby=translation-source-heading]",
                script,
            )

            try:
                await page.wait_for_function(
                    """
                    () => document.querySelector(
                    'd-textarea[aria-labelledby=translation-target-heading]')?.value?.length > 0
                    """,
                    timeout=self.timeout,
                )
            except PlaywrightError as e:
                msg = f"Time limit exceeded. ({self.timeout} ms)"
                raise DeepLCLIPageLoadError(msg) from e

            # Wait for translation to complete (check that [...] placeholder is gone)
            try:
                await page.wait_for_function(
                    """
                    () => {
                        const elem = document.querySelector('d-textarea[aria-labelledby=translation-target-heading]');
                        const text = elem?.value ?? '';
                        return text.length > 0 && !text.includes('[...]');
                    }
                    """,
                    timeout=self.timeout,
                )
            except PlaywrightError as e:
                msg = f"Translation incomplete after {self.timeout} ms"
                raise DeepLCLIPageLoadError(msg) from e

            # Get the translated text directly from the value attribute
            try:
                res = await page.evaluate(
                    """
                    document.querySelector(
                        'd-textarea[aria-labelledby=translation-target-heading]'
                    ).value
                    """,
                )
            except PlaywrightError as e:
                msg = "Unable to get translated text"
                raise DeepLCLIPageLoadError(msg) from e

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
        install(p.chromium, with_deps=True)

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
        )
