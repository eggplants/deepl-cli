# deepl-cli

[![PyPI version](https://badge.fury.io/py/deepl-cli.svg)](https://badge.fury.io/py/deepl-cli) [![Maintainability](https://api.codeclimate.com/v1/badges/a56630914df8538ca93b/maintainability)](https://codeclimate.com/github/eggplants/deepl-cli/maintainability)

- [DeepL Translator](https://www.deepl.com/translator) CLI using Selenium
- Translate standard input into a specified language
- Under development on Ubuntu 20.04 LTS and Python3.8

## Try on Google Cloud Shell

[![Open in Cloud Shell](https://gstatic.com/cloudssh/images/open-btn.png)](https://console.cloud.google.com/cloudshell/open)

```bash
# First, 
$ wget -O - https://gist.githubusercontent.com/eggplants/9996e976fadff8bae9bdfb8628ce07d3/raw/784e9ea1f4385c05c98e1d42840809aec8ca597f/gcp_deeplcli_setup.sh|bash
# example 
$ deepl en:ja < README-cloudshell.txt
```

## Install

```bash
$ pip install deepl-cli
$ sudo apt install chromium-browser chromium-chromedriver python3-selenium -y
$ sudo apt update && sudo apt -f install -y
```

![demo](https://i.imgur.com/mGbwqO7.png)

## Requirements

- Python >= 3.8 (Because of `:=`, Walrus operator)
- [chromium-browser](https://packages.ubuntu.com/ja/source/bionic/chromium-browser)
- [chromium-chromedriver](https://packages.ubuntu.com/ja/bionic/chromium-chromedriver)
- [python3-selenium](https://packages.debian.org/buster/python3-selenium)
- [selenium](https://github.com/SeleniumHQ/selenium)
- [selenium@PyPI](https://pypi.org/project/selenium/)

## Usage

```bash
$ deepl
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
    $ sudo apt update && sudo apt -f install -y
```

## Lisence

MIT

## Author

Haruna(eggplants)
