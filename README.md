# deepl-cli

[![PyPI version](
  <https://badge.fury.io/py/deepl-cli.svg>
  )](
  <https://badge.fury.io/py/deepl-cli>
) [![CI](
  <https://github.com/eggplants/deepl-cli/actions/workflows/ci.yml/badge.svg>
  )](
  <https://github.com/eggplants/deepl-cli/actions/workflows/test.yml>
)


[DeepL Translator](https://www.deepl.com/translator) CLI using [playwright-python](https://github.com/microsoft/playwright-python)

Note: *This project works without DeepL API key. With DeepL API, use [DeepLcom/deepl-python](https://github.com/DeepLcom/deepl-python)*

## Install

```bash
pip install deepl-cli
```

## Usage

### CLI

```shellsession
$ deepl -F en -T ja -s <<<'This tool is useful for me.'
このツールは私にとって役に立ちます。

$ deepl -F ja -T en-US -s <<<'このツールは私にとって便利だ。'
This tool is useful to me.

$ deepl -T ja -s <<<'Heute ist der 22. Februar 2022.'
今日は2022年2月22日です。

$ curl https://example.com | grep -oE '>[^<]+<' | tr -d '><' | sed '1,2d' > txt
$ deepl -f txt -F en -T ja
サンプルドメイン
このドメインは、許可を得ることなくドキュメントの例で使用するためのものです。本番環境での使用は避けてください。
詳細はこちら
```

```shellsession
$ deepl -h
usage: deepl [-h] (-f PATH | -s) -F FR -T TO [-t MS] [--no-headless] [-v] [-V]

DeepL Translator CLI without API Key

options:
  -h, --help            show this help message and exit
  -f PATH, --file PATH  source text file to translate (default: None)
  -s, --stdin           read source text from stdin (default: False)
  -F FR, --fr FR        input language ('auto' to let DeepL detect it) (default: None)
  -T TO, --to TO        output language (default: None)
  -t MS, --timeout MS   timeout interval (default: 100000)
  --no-headless         show the browser window instead of running it headless (default: False)
  -v, --verbose         make output verbose (default: False)
  -V, --version         show program's version number and exit

valid languages of `-F` / --fr`:
{'auto', 'ht', 'ka', 'ml', 'ckb', 'mr', 'ay', 'hr', 'tt', 'ur', 'zh', 'ig', 'hu', 'gl', 'qu', 'tl', 'ln', 'vi', 'bho', 'ga', 'nl', 'scn', 'da', 'fr', 'nb', 'bn', 'mg', 'br', 'mt', 'ceb', 'ts', 'mk', 'ro', 'lmo', 'sl', 'ta', 'az', 'lt', 'sw', 'yi', 'it', 'et', 'st', 'sv', 'mn', 'he', 'gom', 'eu', 'uz', 'pam', 'ar', 'lb', 'te', 'de', 'eo', 'jv', 'ko', 'pa', 'af', 'pl', 'an', 'kmr', 'fa', 'om', 'tr', 'ru', 'tn', 'ha', 'tk', 'ace', 'pt', 'fi', 'sa', 'kk', 'mai', 'xh', 'hy', 'id', 'ps', 'bg', 'cy', 'bs', 'gu', 'el', 'pag', 'my', 'cs', 'ms', 'sr', 'is', 'ba', 'su', 'sq', 'ne', 'ky', 'zu', 'prs', 'yue', 'es', 'oc', 'en', 'sk', 'gn', 'hi', 'as', 'ja', 'ca', 'la', 'lv', 'tg', 'uk', 'mi', 'be', 'wo'}

valid languages of `-T` / `--to`:
{'ht', 'ka', 'ml', 'ckb', 'mr', 'ay', 'hr', 'tt', 'ur', 'zh', 'ig', 'hu', 'gl', 'qu', 'tl', 'ln', 'vi', 'bho', 'ga', 'nl', 'scn', 'da', 'fr', 'nb', 'bn', 'mg', 'br', 'mt', 'ceb', 'zh-Hans', 'ts', 'mk', 'ro', 'lmo', 'sl', 'ta', 'az', 'lt', 'sw', 'yi', 'it', 'et', 'st', 'sv', 'mn', 'en-US', 'he', 'gom', 'eu', 'uz', 'pam', 'ar', 'lb', 'te', 'de', 'es-419', 'eo', 'jv', 'ko', 'pa', 'af', 'pl', 'de-CH', 'an', 'fr-CA', 'pt-PT', 'kmr', 'fa', 'om', 'tr', 'ru', 'zh-Hant', 'tn', 'ha', 'tk', 'ace', 'pt', 'fi', 'sa', 'pt-BR', 'kk', 'mai', 'xh', 'hy', 'id', 'ps', 'bg', 'cy', 'bs', 'gu', 'el', 'pag', 'en-GB', 'my', 'cs', 'ms', 'sr', 'is', 'ba', 'su', 'sq', 'ne', 'ky', 'zu', 'prs', 'yue', 'es', 'oc', 'en', 'sk', 'gn', 'hi', 'as', 'ja', 'ca', 'la', 'lv', 'tg', 'uk', 'mi', 'be', 'wo'}
```

### Package

```python
from deepl import DeepLCLI

deepl = DeepLCLI("en", "ja")
deepl.translate("hello")  # => "こんにちわ"
```

If you use with asyncio, Use `DeepLCLI.translate_async`. See [examples/async.py](https://github.com/eggplants/deepl-cli/blob/master/examples/async.py).

## License

MIT
