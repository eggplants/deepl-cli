# deepl-cli

[![PyPI version](https://badge.fury.io/py/deepl-cli.svg)](https://badge.fury.io/py/deepl-cli) [![Maintainability](https://api.codeclimate.com/v1/badges/a56630914df8538ca93b/maintainability)](https://codeclimate.com/github/eggplants/deepl-cli/maintainability)

- DeepL Translator CLI using Selenium
- Under development on Ubuntu 20.04 LTS

![demo](https://i.imgur.com/aeZv4aV.png)

## Requirements

- Python >= 3.8
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
```
