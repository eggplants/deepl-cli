import sys
from textwrap import dedent
from urllib.request import urlopen

from pyppeteer.browser import Browser
from pyppeteer.errors import TimeoutError
from pyppeteer.launcher import launch
from pyppeteer.page import Page


class DeepLCLIArgCheckingError(Exception):
    pass


class DeepLCLIPageLoadError(Exception):
    pass


class DeepLCLI:

    def __init__(self):
        self.max_length = 5000

    def usage(self) -> None:
        """Print usage."""

        print(dedent('''\
        $ deepl
        SYNTAX:
            $ ... | deepl <from:lang>:<to:lang>
            $ deepl <from:lang>:<to:lang> <<'EOS'
              ...
              EOS
            $ deepl <from:lang>:<to:lang> <<<"..."
            $ deepl <from:lang>:<to:lang> < <filepath>
        USAGE:
            $ echo Hello | deepl en:ja
            $ deepl :ru <<'EOS' # :ru is equivalent of auto:ru
              good morning!
              good night.
              EOS
            $ deepl fr:zh <<<"Mademoiselle"
            $ deepl de:pl < README_de.md
        LANGUAGE CODES:
            <from:lang>: {auto, ja, en, de, fr, es, pt, it, nl, pl, ru, zh}
            <to:lang>:   {ja, en, de, fr, es, pt, it, nl, pl, ru, zh}
        '''))

    def internet_on(self) -> bool:
        """Check an internet connection."""

        try:
            urlopen('https://www.google.com/', timeout=10)
            return True
        except IOError:
            return False

    def validate(self) -> None:
        """Check cmdarg and stdin."""

        fr_langs = {'', 'auto', 'ja', 'en', 'de', 'fr',
                    'es', 'pt', 'it', 'nl', 'pl', 'ru', 'zh'}
        to_langs = fr_langs - {'', 'auto'}

        if (sys.stdin.isatty() and len(sys.argv) == 1) or '-h' in sys.argv:
            # if `$ deepl` or `$ deepl -h`
            self.usage()
            exit(0)

        if sys.stdin.isatty():
            # raise err if stdin is empty
            raise DeepLCLIArgCheckingError('stdin seems to be empty.')

        num_opt = len(sys.argv[1::])
        if num_opt != 1:
            # raise err if arity != 1
            raise DeepLCLIArgCheckingError(
                'num of option is wrong(given %d, expected 1).' % num_opt)

        opt_lang = sys.argv[1].split(':')
        if len(opt_lang) != 2 or opt_lang[0] not in fr_langs \
                or opt_lang[1] not in to_langs:
            # raise err if specify 2 langs is empty
            raise DeepLCLIArgCheckingError('correct your lang format.')

        if opt_lang[0] == opt_lang[1]:
            # raise err if <fr:lang> == <to:lang>
            raise DeepLCLIArgCheckingError('two languages cannot be same.')

        scripts = sys.stdin.read()
        if len(scripts) > self.max_length:
            # raise err if stdin > self.max_length chr
            raise DeepLCLIArgCheckingError(
                'limit of script is less than {} chars(Now: {} chars).'.format(
                    self.max_length, len(scripts)))

        self.fr_lang = ('auto' if opt_lang[0] == ''
                        else opt_lang[0]
                        )[0]
        self.to_lang = opt_lang[1]
        self.scripts = scripts.rstrip("\n")

    async def translate(self) -> str:
        """Open a deepl page and throw a request."""

        if not self.internet_on():
            raise DeepLCLIPageLoadError('Your network seem to be offline.')

        browser: Browser = await launch()
        page: Page = await browser.newPage()
        userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6)'\
                    'AppleWebKit/537.36 (KHTML, like Gecko) '\
                    'Chrome/77.0.3864.0 Safari/537.36'
        await page.setUserAgent(userAgent)

        await page.goto(
            'https://www.deepl.com/translator#{}/{}/_'.format(
                self.fr_lang, self.to_lang))
        try:
            page.waitForSelector(
                '#dl_translator > div.lmt__text', timeout=15000)
        except TimeoutError:
            raise DeepLCLIPageLoadError

        input_area = await page.J('textarea[dl-test=translator-source-input]')
        await page.evaluate('''
            () => document.querySelector(
                'textarea[dl-test=translator-source-input]').value = ""
        ''')
        await input_area.type(self.scripts)
        try:
            await page.waitForFunction('''
                () => document.querySelector(
                'textarea[dl-test=translator-target-input]').value !== ""
            ''')
        except TimeoutError:
            raise DeepLCLIPageLoadError

        output_area = await page.J(
            'textarea[dl-test="translator-target-input"]')
        res = await page.evaluate('elm => elm.value', output_area)
        await browser.close()
        return res.rstrip("\n")
