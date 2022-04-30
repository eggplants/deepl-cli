import asyncio
from typing import Optional
from urllib.parse import quote
from urllib.request import urlopen

from pyppeteer.browser import Browser  # type: ignore[import]
from pyppeteer.errors import TimeoutError  # type: ignore[import]
from pyppeteer.launcher import launch  # type: ignore[import]
from pyppeteer.page import Page  # type: ignore[import]


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
        "zh",
    }
    to_langs = fr_langs - {"auto"}

    def __init__(self, fr_lang: str, to_lang: str) -> None:
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
        self.translated_fr_lang: Optional[str] = None
        self.translated_to_lang: Optional[str] = None
        self.max_length = 5000

    def internet_on(self) -> bool:
        """Check an internet connection."""
        try:
            urlopen("http://www.google.com/", timeout=10)
            return True
        except IOError:
            return False

    def _chk_script(self, script: str) -> str:
        """Check cmdarg and stdin."""
        script = script.rstrip("\n")
        if self.max_length is not None and len(script) > self.max_length:
            # raise err if stdin > self.max_length chr
            raise DeepLCLIError(
                "Limit of script is less than {} chars(Now: {} chars).".format(
                    self.max_length, len(script)
                )
            )
        elif len(script) <= 0:
            # raise err if stdin <= 0 chr
            raise DeepLCLIError("Script seems to be empty.")
        else:
            return script

    def translate(self, script: str) -> str:
        if not self.internet_on():
            raise DeepLCLIPageLoadError("Your network seem to be offline.")
        self._chk_script(script)
        script = quote(script.replace("/", r"\/"), safe="")
        return asyncio.get_event_loop().run_until_complete(self._translate(script))

    async def _translate(self, script: str) -> str:
        """Throw a request."""
        browser: Browser = await launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--single-process",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--no-zygote",
            ],
        )
        page: Page = await browser.newPage()
        userAgent = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6)"
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/77.0.3864.0 Safari/537.36"
        )
        await page.setUserAgent(userAgent)
        hash = f"#{self.fr_lang}/{self.to_lang}/{script}"
        await page.goto("https://www.deepl.com/translator" + hash)
        try:
            page.waitForSelector("#dl_translator > div.lmt__text", timeout=15000)
        except TimeoutError:
            raise DeepLCLIPageLoadError("Time limit exceeded. (30000ms)")

        try:
            await page.waitForFunction(
                """
                () => document.querySelector(
                'textarea[dl-test=translator-target-input]').value !== ""
            """
            )
            await page.waitForFunction(
                """
                () => !document.querySelector(
                'textarea[dl-test=translator-target-input]').value.includes("[...]")
            """
            )
            await page.waitForFunction(
                """
                () => document.querySelector("[dl-test='translator-source-input']") !== null
            """
            )
            await page.waitForFunction(
                """
                () => document.querySelector("[dl-test='translator-target-lang']") !== null
            """
            )
        except TimeoutError:
            raise DeepLCLIPageLoadError("Time limit exceeded. (30000ms)")

        output_area = await page.J('textarea[dl-test="translator-target-input"]')
        res = await page.evaluate("elm => elm.value", output_area)
        self.translated_fr_lang = str(
            await page.evaluate(
                """() => {
            return document.querySelector("[dl-test='translator-source-input']").lang
            }"""
            )
        ).split("-")[0]

        self.translated_to_lang = str(
            await page.evaluate(
                """() => {
            return document.querySelector("[dl-test='translator-target-lang']").getAttribute("dl-selected-lang")
            }"""
            )
        ).split("-")[0]
        await browser.close()
        if type(res) is str:
            return res.rstrip("\n")
        else:
            raise ValueError(
                f"Invalid response. Type of response must be str, got {type(res)})"
            )
