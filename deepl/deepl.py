from __future__ import annotations

import asyncio
from urllib.parse import quote

from install_playwright import install
from playwright._impl._api_types import Error as PlaywrightError
from playwright.async_api import async_playwright


class DeepLCLIError(Exception):
    pass


class DeepLCLIPageLoadError(Exception):
    pass


class DeepLCLI:
    fr_langs = {
        "auto",
        "bg",
        "cs",
        "da",
        "de",
        "el",
        "en",
        "es",
        "et",
        "fi",
        "fr",
        "hu",
        "id",
        "it",
        "ja",
        "lt",
        "lv",
        "nl",
        "pl",
        "pt",
        "ro",
        "ru",
        "sk",
        "sl",
        "sv",
        "tr",
        "uk",
        "zh",
    }
    to_langs = fr_langs - {"auto"}

    def __init__(self, fr_lang: str, to_lang: str, timeout: int = 15000) -> None:
        if fr_lang not in self.fr_langs:
            raise DeepLCLIError(
                f"{repr(fr_lang)} is not valid language. Valid language:\n"
                + repr(self.fr_langs)
            )
        elif to_lang not in self.to_langs:
            raise DeepLCLIError(
                f"{repr(to_lang)} is not valid language. Valid language:\n"
                + repr(self.to_langs)
            )

        self.fr_lang = fr_lang
        self.to_lang = to_lang
        self.translated_fr_lang: str | None = None
        self.translated_to_lang: str | None = None
        self.max_length = 5000
        self.timeout = timeout

    def translate(self, script: str) -> str:
        script = self.__sanitize_script(script)
        return asyncio.run(self.__translate(script))

    async def __translate(self, script: str) -> str:
        """Throw a request."""
        async with async_playwright() as p:
            install(p.chromium)
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--single-process",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--no-zygote",
                    "--window-size=1920,1080",
                ],
            )

            page = await browser.new_page()
            page.set_default_timeout(self.timeout)

            await page.goto(
                f"https://www.deepl.com/en/translator#{self.fr_lang}/{self.to_lang}/{script}"
            )

            # Wait for loading to complete
            try:
                page.get_by_role("main")
            except PlaywrightError as e:
                raise DeepLCLIPageLoadError(
                    f"Maybe Time limit exceeded. ({self.timeout} ms, {e})"
                )

            # Wait for translation to complete
            try:
                await page.wait_for_function(
                    """
                    () => document.querySelector(
                    'textarea[dl-test=translator-target-input]').value !== ""
                """
                )
                await page.wait_for_function(
                    """
                    () => !document.querySelector(
                    'textarea[dl-test=translator-target-input]').value.includes("[...]")
                """
                )
                await page.wait_for_function(
                    """
                    () => document.querySelector("[dl-test='translator-source-input']") !== null
                """
                )
            except PlaywrightError as e:
                raise DeepLCLIPageLoadError(
                    f"Time limit exceeded. ({self.timeout} ms, {e})"
                )

            # Get information
            input_textbox = page.get_by_role("textbox", name="Source text")
            output_textbox = page.get_by_role("textbox", name="Translation results")

            self.translated_fr_lang = str(
                await input_textbox.get_attribute("lang")
            ).split("-")[0]
            self.translated_to_lang = str(
                await output_textbox.get_attribute("lang")
            ).split("-")[0]

            res = str(await output_textbox.input_value())

            await browser.close()

            return res.rstrip("\n")

    def __sanitize_script(self, script: str) -> str:
        """Check command line args and stdin."""
        script = script.rstrip("\n")

        if self.max_length is not None and len(script) > self.max_length:
            raise DeepLCLIError(
                f"Limit of script is less than {self.max_length} chars"
                f"(Now: {len(script)} chars)"
            )

        if len(script) <= 0:
            raise DeepLCLIError("Script seems to be empty.")

        return quote(script.replace("/", r"\/").replace("|", r"\|"), safe="")
