#!/usr/bin/python
import sys
import time

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
        print(
        'SYNTAX:',
        '    $ stdin | python3 test.py <from:lang>:<to:lang>',
        'USAGE',
        '    $ echo Hello | python3 test.py en:ja',
        'LANGUAGE CODES:',
        '    <from:lang>: {auto, ja, en, de, fr, es, pt, it, nl, pl, ru, zh}',
        '    <to:lang>:   {ja, en, de, fr, es, pt, it, nl, pl, ru, zh}',
        'TIPS:',
        '    To use this, run:',
        '    $ sudo apt install chromium-browser chromium-chromedriver python3-selenium -y',
        '    $ sudo apt update && sudo apt -f install -y',
        '    $ pip install selenium',
        sep="\n"
    )

    def validate(self):
        # <fr:lang> ::= {auto, ja, en, de, fr, es, pt, it, nl, pl, ru, zh}
        fr_langs = {'auto', 'ja', 'en', 'de', 'fr', 'es', 'pt', 'it', 'nl', 'pl', 'ru', 'zh'}
        # <to:lang> ::= <fr:lang> - {auto}
        to_langs = fr_langs - {'auto'}
        # if `$ deepl-cli`
        if sys.stdin.isatty() and len(sys.argv) == 1:
            self.usage()
            exit(0)
        # raise err if stdin is empty
        if sys.stdin.isatty():
            raise DeepLCLIArgCheckingError('stdin seems to be empty.')
        # raise err if arity != 1
        num_opt = len(sys.argv[1::])
        if num_opt != 1:
            raise DeepLCLIArgCheckingError('num of option is wrong(given %d, expected 1).'%num_opt)
        # raise err if specify 2 langs is empty
        opt_lang = sys.argv[1].split(':')
        if len(opt_lang) != 2 or opt_lang[0] not in fr_langs or opt_lang[1] not in to_langs:
            raise DeepLCLIArgCheckingError('correct your lang format.')
        # raise err if <fr:lang> == <to:lang>
        fr_lang, to_lang = opt_lang
        if fr_lang == to_lang:
            raise DeepLCLIArgCheckingError('two languages cannot be same.')
        # raise err if stdin > 5000 chr
        scripts = sys.stdin.read()
        if len(scripts) > 5000:
            raise DeepLCLIArgCheckingError('limit of script is less than 5000 chars(Now: %d chars).'%len(scripts))

        self.fr_lang = fr_lang
        self.to_lang = to_lang
        self.scripts = scripts

    def translate(self):
        o = Options()
        o.add_argument('--headless')
        o.add_argument('--disable-gpu')
        o.add_argument('--user-agent='\
            'Mozilla/5.0 (iPhone; CPU iPhone OS 10_2 like Mac OS X) '\
            'AppleWebKit/602.3.12 (KHTML, like Gecko) Version/10.0 Mobile/14C92 Safari/602.1'
        )
        d = webdriver.Chrome(options=o)
        d.get('https://www.deepl.com/translator#%s/%s'%(self.fr_lang, self.to_lang))
        try:
            WebDriverWait(d, 15).until(
                EC.presence_of_all_elements_located
            )
        except TimeoutException as te:
            raise DeepLCLIPageLoadError(te)

        i_xpath = '//textarea[@dl-test="translator-source-input"]'
        input_textarea = d.find_element_by_xpath(i_xpath)
        input_textarea.send_keys(self.scripts)
        # Wait for the translation process
        time.sleep(10) # fix needed
        o_xpath = '//textarea[@dl-test="translator-target-input"]'
        res = d.find_element_by_xpath(o_xpath).get_attribute('value')
        d.quit()
        return res.rstrip()

def main():
    t = DeepLCLI()
    t.validate()
    print(t.translate())

if __name__ == "__main__":
    main()
