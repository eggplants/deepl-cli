import asyncio
import sys
from textwrap import dedent
from typing import List, Optional, Tuple
from urllib.parse import quote
from urllib.request import urlopen

from pyppeteer.browser import Browser  # type: ignore
from pyppeteer.errors import TimeoutError  # type: ignore
from pyppeteer.launcher import launch  # type: ignore
from pyppeteer.page import Page  # type: ignore


class DeepLCLIArgCheckingError(Exception):
    pass


class DeepLCLIPageLoadError(Exception):
    pass


class DeepLCLI:

    def __init__(self, langs: Optional[Tuple[str, str]] = None) -> None:
        if langs:
            self.fr_lang, self.to_lang = self._chk_lang(langs)
        self.max_length = 5000

    def usage(self) -> None:
        """Print usage."""

        print(dedent('''\
        $ deepl
        SYNTAX:
            $ ... | deepl <from:lang>:<to:lang>
            $ deepl <from:lang>:<to:lang> << 'EOS'
              ...
              EOS
            $ deepl <from:lang>:<to:lang> <<< "..."
            $ deepl <from:lang>:<to:lang> < <filepath>
        USAGE:
            $ echo Hello | deepl en:ja
            $ deepl :ru << 'EOS' # :ru is equivalent of auto:ru
              good morning!
              good night.
              EOS
            $ deepl fr:zh <<< "Mademoiselle"
            $ deepl de:pl < README_de.md
        LANGUAGE CODES:
            <from:lang>: {auto it et nl el sv es sk sl cs da
                          de hu fi fr bg pl pt lv lt ro ru en zh ja}
            <to:lang>:   {it et nl el sv es sk sl cs da
                          de hu fi fr bg pl pt lv lt ro ru en zh ja}
        '''))

    def internet_on(self) -> bool:
        """Check an internet connection."""
        try:
            urlopen('http://www.google.com/', timeout=10)
            return True
        except IOError:
            return False

    def _chk_stdin(self) -> None:
        """Check if stdin is entered."""
        if (sys.stdin.isatty() and len(sys.argv) == 1) or '-h' in sys.argv:
            # if `$ deepl` or `$ deepl -h`
            self.usage()
            sys.tracebacklimit = 0
            raise DeepLCLIArgCheckingError('show help.')
        elif sys.stdin.isatty():
            # raise err if stdin is empty
            raise DeepLCLIArgCheckingError('stdin seems to be empty.')

    # def _chk_auth(self) -> None:
    #     """Check if login is required."""
    #     self.max_length = 5000

    def _chk_argnum(self, args: List[str]) -> None:
        """Check if num of args are valid."""
        num_opt = len(args)
        if num_opt != 1:
            # raise err if arity != 1
            raise DeepLCLIArgCheckingError(
                'num of option is wrong(given %d, expected 1 or 2).' % num_opt)

    def _chk_lang(self, in_lang: Tuple[str, str]) -> Tuple[str, str]:
        """Check if language options are valid."""
        fr_langs = {'auto', 'it', 'et', 'nl', 'el',
                    'sv', 'es', 'sk', 'sl', 'cs',
                    'da', 'de', 'hu', 'fi', 'fr',
                    'bg', 'pl', 'pt', 'lv', 'lt',
                    'ro', 'ru', 'en', 'zh', 'ja', ''}
        to_langs = fr_langs - {'', 'auto'}

        if len(in_lang) != 2 or in_lang[0] not in fr_langs \
                or in_lang[1] not in to_langs:
            # raise err if specify 2 langs is empty
            raise DeepLCLIArgCheckingError('correct your lang format.')

        if in_lang[0] == in_lang[1]:
            # raise err if <fr:lang> == <to:lang>
            raise DeepLCLIArgCheckingError('two languages cannot be same.')

        fr = ('auto' if in_lang[0] == ''
              else in_lang[0])
        to = in_lang[1]

        return (fr, to)

    def chk_cmdargs(self) -> None:
        """Check cmdargs and configurate languages.(for using as a command)"""
        self._chk_stdin()
        self._chk_argnum(sys.argv[1::])
        # self._chk_auth()

    def _chk_script(self, script: str) -> str:
        """Check cmdarg and stdin."""

        script = script.rstrip("\n")

        if self.max_length is not None and len(script) > self.max_length:
            # raise err if stdin > self.max_length chr
            raise DeepLCLIArgCheckingError(
                'limit of script is less than {} chars(Now: {} chars).'.format(
                    self.max_length, len(script)))
        if len(script) <= 0:
            # raise err if stdin <= 0 chr
            raise DeepLCLIArgCheckingError('script seems to be empty.')

        return script

    def translate(self, script: str) -> str:
        if not self.internet_on():
            raise DeepLCLIPageLoadError('Your network seem to be offline.')
        self.fr_lang, self.to_lang = self._chk_lang(
            (self.fr_lang, self.to_lang))
        self._chk_script(script)
        script = quote(script, safe='')
        return asyncio.get_event_loop().run_until_complete(
            self._translate(script))

    async def _translate(self, script: str) -> str:
        """Throw a request."""
        browser: Browser = await launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--single-process',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--no-zygote'

            ])
        page: Page = await browser.newPage()
        userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6)'\
                    'AppleWebKit/537.36 (KHTML, like Gecko) '\
                    'Chrome/77.0.3864.0 Safari/537.36'
        await page.setUserAgent(userAgent)
        await page.goto(
            'https://www.deepl.com/translator#{}/{}/{}'.format(
                self.fr_lang, self.to_lang, script))
        try:
            page.waitForSelector(
                '#dl_translator > div.lmt__text', timeout=15000)
        except TimeoutError:
            raise DeepLCLIPageLoadError

        try:
            await page.waitForFunction('''
                () => document.querySelector(
                'textarea[dl-test=translator-target-input]').value !== ""
            ''')
            await page.waitForFunction('''
                () => !document.querySelector(
                'textarea[dl-test=translator-target-input]').value.includes("[...]")
            ''')
        except TimeoutError:
            raise DeepLCLIPageLoadError

        output_area = await page.J(
            'textarea[dl-test="translator-target-input"]')
        res = await page.evaluate('elm => elm.value', output_area)
        await browser.close()
        return res.rstrip('\n')
