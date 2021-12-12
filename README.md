# deepl-cli

[![Release Package](https://github.com/eggplants/deepl-cli/workflows/Release%20Package/badge.svg)](https://github.com/eggplants/deepl-cli/actions/runs/345738487) [![PyPI version](https://badge.fury.io/py/deepl-cli.svg)](https://badge.fury.io/py/deepl-cli)
[![Maintainability](https://api.codeclimate.com/v1/badges/a56630914df8538ca93b/maintainability)](https://codeclimate.com/github/eggplants/deepl-cli/maintainability)

[![MIT License](http://img.shields.io/badge/license-MIT-blue.svg?style=flat)](LICENSE)

[![Downloads](https://pepy.tech/badge/deepl-cli)](https://pepy.tech/project/deepl-cli) [![Downloads](https://pepy.tech/badge/deepl-cli/month)](https://pepy.tech/project/deepl-cli/month) [![Downloads](https://pepy.tech/badge/deepl-cli/week)](https://pepy.tech/project/deepl-cli/week)

- [DeepL Translator](https://www.deepl.com/translator) CLI using [Pyppeteer](https://github.com/pyppeteer/pyppeteer)
- Translate standard input into a specified language

Note: *This project works without DeepL API key. With DeepL API, use [DeepLcom/deepl-python](https://github.com/DeepLcom/deepl-python)*

## Install

```bash
# python >=3.5,<3.10
pip install deepl-cli
```

![demo](https://i.imgur.com/mGbwqO7.png)

## Docker Image

- DockerHub: <https://hub.docker.com/r/eggplanter/deepl-cli>

```bash
# TRY
docker run -it --rm eggplanter/deepl-cli:0.1
```

## Requirements

- [Python>=3.5](https://www.python.org/ftp/python/)
- [pyppeteer](https://github.com/pyppeteer/pyppeteer)

## Usage

## from CLI

```shellsession
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
```

## from Package

```python
from deepl import deepl

t = deepl.DeepLCLI(langs=('en', 'ja'))
t.translate('hello') #=> 'こんにちわ'
```

## Lisence

MIT

## Author

Haruna(eggplants)
