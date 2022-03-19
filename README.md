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
pip install deepl-cli
```

![demo](https://i.imgur.com/mGbwqO7.png)

## Docker Image

- DockerHub: <https://hub.docker.com/r/eggplanter/deepl-cli>

```bash
docker run -it --rm eggplanter/deepl-cli:0.1
```

## Requirements

- [Python>=3.5](https://www.python.org/ftp/python/)
- [pyppeteer](https://github.com/pyppeteer/pyppeteer)

## Usage

## from CLI

```shellsession
$ deepl -h
usage: deepl [-h] (-f PATH | -s) [--fr FR] --to TO [-v]

DeepL Translator CLI without API Key

optional arguments:
  -h, --help            show this help message and exit
  -f PATH, --file PATH  source text file to translate (default: None)
  -s, --stdin           read source text from stdin (default: False)
  --fr FR               input language (default: auto)
  --to TO               output language (default: None)
  -v, --version         show program's version number and exit

valid languages of `--fr`:
{'ja', 'el', '', 'lv', 'es', 'ru', 'it', 'cs', 'lt', 'sk', 'bg', 'da', 'et', 'pl', 'sl', 'ro', 'pt', 'zh', 'hu', 'auto', 'sv', 'de', 'nl', 'en', 'fi', 'fr'}

valid languages of `--to`:
{'ja', 'el', 'lv', 'es', 'ru', 'it', 'cs', 'lt', 'sk', 'bg', 'da', 'et', 'pl', 'sl', 'ro', 'pt', 'zh', 'hu', 'sv', 'de', 'nl', 'en', 'fi', 'fr'}
```

## from Package

```python
from deepl import deepl

t = deepl.DeepLCLI("en", "ja")
t.translate("hello") #=> "こんにちわ"
```

## Lisence

MIT

## Author

Haruna(eggplants)
