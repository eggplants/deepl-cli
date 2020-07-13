#!/usr/bin/python
import os
import sys
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class DeepLCLIArgCheckingError(Exception):
    pass

def usage():
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

# <fr:lang> ::= {auto, ja, en, de, fr, es, pt, it, nl, pl, ru, zh}
fr_langs = {'auto', 'ja', 'en', 'de', 'fr', 'es', 'pt', 'it', 'nl', 'pl', 'ru', 'zh'}
# <to:lang> ::= <fr:lang> - {auto}
to_langs = fr_langs - {'auto'}
# if `$ deepl-cli`
if sys.stdin.isatty() and len(sys.argv) == 1:
    usage()
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
    raise DeepLCLIArgCheckingError('limit of script is less than 5000 chars(Now: ).'%len(scripts))

# else input

o = Options()
o.add_argument('--headless')
o.add_argument('--disable-gpu')
o.add_argument('--user-agent='\
    'Mozilla/5.0 (iPhone; CPU iPhone OS 10_2 like Mac OS X) '\
    'AppleWebKit/602.3.12 (KHTML, like Gecko) Version/10.0 Mobile/14C92 Safari/602.1'
)

d = webdriver.Chrome(options=o)
d.get('https://www.deepl.com/translator#%s/%s'%(fr_lang, to_lang))
# input: scripts
time.sleep(3)
i_xpath = '//textarea[@dl-test="translator-source-input"]'
input_textarea = d.find_element_by_xpath(i_xpath)
input_textarea.send_keys(scripts)
time.sleep(10)
o_xpath = '//textarea[@dl-test="translator-target-input"]'
res = d.find_element_by_xpath(o_xpath).get_attribute('value')
print(res)
d.quit()
