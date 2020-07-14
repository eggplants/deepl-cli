# deepl-cli

[![PyPI version](https://badge.fury.io/py/deepl-cli.svg)](https://badge.fury.io/py/deepl-cli) [![Maintainability](https://api.codeclimate.com/v1/badges/a56630914df8538ca93b/maintainability)](https://codeclimate.com/github/eggplants/deepl-cli/maintainability) [![MIT License](http://img.shields.io/badge/license-MIT-blue.svg?style=flat)](LICENSE)

[![Downloads](https://pepy.tech/badge/deepl-cli)](https://pepy.tech/project/deepl-cli) [![Downloads](https://pepy.tech/badge/deepl-cli/month)](https://pepy.tech/project/deepl-cli/month) [![Downloads](https://pepy.tech/badge/deepl-cli/week)](https://pepy.tech/project/deepl-cli/week)

- [DeepL Translator](https://www.deepl.com/translator) CLI using Selenium
- Translate standard input into a specified language
- Under development on Ubuntu 20.04 LTS and Python3.8

## Try on Google Cloud Shell

[![Open in Cloud Shell](https://gstatic.com/cloudssh/images/open-btn.png)](https://console.cloud.google.com/cloudshell/open?git_repo=https://github.com/eggplants/deepl-cli&tutorial=README.md&shellonly=true)

```bash
# First,
$ wget -O - https://raw.githubusercontent.com/eggplants/deepl-cli/master/deeplcli_setup.sh | bash
# example
$ deepl en:ja < README-cloudshell.txt
```

## Install

```bash
$ wget -O - https://raw.githubusercontent.com/eggplants/deepl-cli/master/deeplcli_setup.sh | bash
```

![demo](https://i.imgur.com/mGbwqO7.png)

## Requirements

- [Python >= 3.8](https://www.python.org/ftp/python/)
    - (Because of `:=`, Walrus operator)
- [google-chrome >= 83](https://www.google.com/chrome/?platform=linux)
- [chromedriver >= 83](https://chromedriver.chromium.org/downloads)
- [selenium](https://pypi.org/project/selenium/)

## Usage

```bash
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
