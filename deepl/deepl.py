#!/usr/bin/env python 3.8
import sys
import time
from textwrap import dedent
from urllib.request import urlopen

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class DeepLCLIArgCheckingError(Exception):
    pass

class DeepLCLIPageLoadError(Exception):
    pass

class DeepLCLI:

    def usage(self):
        """Print usage."""

        print(
            dedent('''\
                SYNTAX:
                    $ (...) | deepl <from:lang>:<to:lang>
                    $ deepl <from:lang>:<to:lang> <<'EOS'
                      (...)
                      EOS
                    $ deepl <from:lang>:<to:lang> <<<"(...)"
                USAGE:
                    $ echo Hello | deepl en:ja
                    $ deepl :ru <<'EOS' # :ru is equivalent of auto:ru
                      good morning!
                      good night.
                      EOS
                    $ deepl fr:zh <<<"Mademoiselle"
                LANGUAGE CODES:
                    <from:lang>: {(empty)=auto, ja, en, de, fr, es, pt, it, nl, pl, ru, zh}
                    <to:lang>:   {ja, en, de, fr, es, pt, it, nl, pl, ru, zh}
                TIPS:
                    To use this, run:
                    $ sudo apt install chromium-browser chromium-chromedriver python3-selenium -y
                    $ sudo apt update && sudo apt -f install -y''')
        )

    def internet_on(self):
        """Check an internet connection."""

        try:
            response = urlopen('https://www.google.com/', timeout=10)
            return True
        except:
            return False

    def validate(self):
        """Check cmdarg and stdin."""

        fr_langs = {'', 'auto', 'ja', 'en', 'de', 'fr', 'es', 'pt', 'it', 'nl', 'pl', 'ru', 'zh'}
        to_langs = fr_langs - {'', 'auto'}

        if sys.stdin.isatty() and len(sys.argv) == 1:
            # if `$ deepl`
            self.usage()
            exit(0)

        if sys.stdin.isatty():
            # raise err if stdin is empty
            raise DeepLCLIArgCheckingError('stdin seems to be empty.')

        if (num_opt := len(sys.argv[1::])) != 1:
            # raise err if arity != 1
            raise DeepLCLIArgCheckingError('num of option is wrong(given %d, expected 1).'%num_opt)

        if len(opt_lang := sys.argv[1].split(':')) != 2 or opt_lang[0] not in fr_langs or opt_lang[1] not in to_langs:
            # raise err if specify 2 langs is empty
            raise DeepLCLIArgCheckingError('correct your lang format.')

        if opt_lang[0] == opt_lang[1]:
            # raise err if <fr:lang> == <to:lang>
            raise DeepLCLIArgCheckingError('two languages cannot be same.')

        if len(scripts := sys.stdin.read()) > 5000:
            # raise err if stdin > 5000 chr
            raise DeepLCLIArgCheckingError('limit of script is less than 5000 chars(Now: %d chars).'%len(scripts))

        self.fr_lang = ('auto' if   opt_lang[0] == ''
                               else opt_lang[0]
                       )[0]
        self.to_lang = opt_lang[1]
        self.scripts = scripts

    def translate(self):
        """Open a deepl page and throw a request."""

        if not self.internet_on():
            raise DeepLCLIPageLoadError('Your network seem to be offline.')

        o = Options()
        o.add_argument('--headless')    # if commented. window will be open
        o.add_argument('--disable-gpu') # if commented, window will be open
        o.add_argument('--user-agent='\
            'Mozilla/5.0 (iPhone; CPU iPhone OS 10_2 like Mac OS X) '\
            'AppleWebKit/602.3.12 (KHTML, like Gecko) Version/10.0 Mobile/14C92 Safari/602.1'
        )

        d = webdriver.Chrome(options=o)
        d.get('https://www.deepl.com/translator#%s/%s/_'%(self.fr_lang, self.to_lang))
        try:
            WebDriverWait(d, 15).until(
                EC.presence_of_all_elements_located
            )
        except TimeoutException as te:
            raise DeepLCLIPageLoadError(te)

        input_area = d.find_element_by_xpath(
            '//textarea[@dl-test="translator-source-input"]'
        )
        input_area.clear()
        input_area.send_keys(self.scripts)

        # Wait for the translation process
        time.sleep(10) # fix needed

        output_area = d.find_element_by_xpath(
            '//textarea[@dl-test="translator-target-input"]'
        )
        res = output_area.get_attribute('value').rstrip()
        d.quit()
        return res
