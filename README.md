# deepl-cli

[![Release Package](
  <https://github.com/eggplants/deepl-cli/workflows/Release%20Package/badge.svg>
  )](
  <https://github.com/eggplants/deepl-cli/actions/workflows/release.yml>
) [![Test](
  <https://github.com/eggplants/deepl-cli/actions/workflows/test.yml/badge.svg>
  )](
  <https://github.com/eggplants/deepl-cli/actions/workflows/test.yml>
) [![PyPI version](
  <https://badge.fury.io/py/deepl-cli.svg>
  )](
  <https://badge.fury.io/py/deepl-cli>
)

[![Maintainability](
  <https://api.codeclimate.com/v1/badges/a56630914df8538ca93b/maintainability>
  )](
  <https://codeclimate.com/github/eggplants/deepl-cli/maintainability>
) [![pre-commit.ci status](
  <https://results.pre-commit.ci/badge/github/eggplants/deepl-cli/master.svg>
  )](
  <https://results.pre-commit.ci/latest/github/eggplants/deepl-cli/master>
)

![image](https://user-images.githubusercontent.com/42153744/159145088-752decf7-8736-44c3-86aa-37fd0cee83df.png)

- [DeepL Translator](https://www.deepl.com/translator) CLI using [playwright-python](https://github.com/microsoft/playwright-python)

Note: *This project works without DeepL API key. With DeepL API, use [DeepLcom/deepl-python](https://github.com/DeepLcom/deepl-python)*

## Install

```bash
pip install deepl-cli
```

## Usage

## CLI

```shellsession
$ deepl -h
usage: deepl [-h] (-f PATH | -s) [--fr FR] --to TO [-t MS] [-v] [-V]

DeepL Translator CLI without API Key

optional arguments:
  -h, --help            show this help message and exit
  -f PATH, --file PATH  source text file to translate (default: None)
  -s, --stdin           read source text from stdin (default: False)
  --fr FR               input language (default: auto)
  --to TO               output language (default: None)
  -t MS, --timeout MS   timeout interval (default: 5000)
  -v, --verbose         make output verbose (default: False)
  -V, --version         show program's version number and exit

valid languages of `--fr`:
{'fi', 'cs', 'lv', 'nl', 'el', 'auto', 'ru', 'da', 'sv', 'it', 'uk', 'zh', 'ko', 'et', 'de', 'en', 'es', 'bg', 'lt', 'ja', 'pl', 'tr', 'id', 'sk', 'sl', 'hu', 'fr', 'ro', 'pt'}

valid languages of `--to`:
{'fi', 'cs', 'lv', 'nl', 'lt', 'ja', 'el', 'pl', 'ru', 'tr', 'da', 'sv', 'pt', 'id', 'it', 'sk', 'sl', 'hu', 'fr', 'uk', 'zh', 'ko', 'et', 'de', 'en', 'ro', 'es', 'bg'}
```

## Package

```python
from deepl import DeepLCLI

deepl = DeepLCLI("en", "ja")
deepl.translate("hello") #=> "こんにちわ"
```

If you use with asyncio, Use `DeepLCLI.translate_async`. See [examples/async.py](https://github.com/eggplants/deepl-cli/blob/master/examples/async.py).

## License

MIT
