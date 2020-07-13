# deepl-cli

- DeepL Translator CLI using Selenium (Experimental)
- Under development on Ubuntu 20.04 LTS

![demo](https://i.imgur.com/aeZv4aV.png)

## Requirements

- [chromium-browser](https://packages.ubuntu.com/ja/source/bionic/chromium-browser)
- [chromium-chromedriver](https://packages.ubuntu.com/ja/bionic/chromium-chromedriver)
- [python3-selenium](https://packages.debian.org/buster/python3-selenium)
- [selenium](https://github.com/SeleniumHQ/selenium)
- [selenium@PyPI](https://pypi.org/project/selenium/)

```bash
SYNTAX:
    $ stdin | python3 test.py <from:lang>:<to:lang>
USAGE
    $ echo Hello | python3 test.py en:ja
LANGUAGE CODES:
    <from:lang>: {auto, ja, en, de, fr, es, pt, it, nl, pl, ru, zh}
    <to:lang>:   {ja, en, de, fr, es, pt, it, nl, pl, ru, zh}
TIPS:
    To use this, run:
    $ sudo apt install chromium-browser chromium-chromedriver python3-selenium -y
    $ sudo apt update && sudo apt -f install -y
    $ pip install selenium
```
