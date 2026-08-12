"""Language codes supported by DeepL.

How to get language list:

1. Open input language dropdown and run on console:

```js
const fr = Array.from(document.querySelectorAll(`[data-testid^='translator-lang-option']`))
  .map(e=>e.getAttribute('data-testid').replace(/^translator-lang-option-/, ''))
  .filter(e=>!e.endsWith('-pin'))
```

2. Open output language dropdown and run on console:

```js
const to = Array.from(document.querySelectorAll(`[data-testid^='translator-lang-option']`))
  .map(e=>e.getAttribute('data-testid').replace(/^translator-lang-option-/, ''))
  .filter(e=>!e.endsWith('-pin'))
```

3. Compare the two lists to find languages that are only in one of them:

```js
new Set(fr.sort()) // FR_LANGS
new Set(to.sort()).difference(new Set(fr.sort())) // TO_ONLY
new Set(fr.sort()).difference(new Set(to.sort())) // FR_ONLY
```
"""

from typing import Final

# DeepL's own code for the "Detect language" entry at the top of the source dropdown.
# It is a source language only: there is nothing to detect about the output.
AUTO_LANG: Final[str] = "auto"

FR_LANGS: Final[set[str]] = {
    "ace",
    "af",
    "an",
    "ar",
    "as",
    "auto",
    "ay",
    "az",
    "ba",
    "be",
    "bg",
    "bho",
    "bn",
    "br",
    "bs",
    "ca",
    "ceb",
    "ckb",
    "cs",
    "cy",
    "da",
    "de",
    "el",
    "en",
    "eo",
    "es",
    "et",
    "eu",
    "fa",
    "fi",
    "fr",
    "ga",
    "gl",
    "gn",
    "gom",
    "gu",
    "ha",
    "he",
    "hi",
    "hr",
    "ht",
    "hu",
    "hy",
    "id",
    "ig",
    "is",
    "it",
    "ja",
    "jv",
    "ka",
    "kk",
    "kmr",
    "ko",
    "ky",
    "la",
    "lb",
    "lmo",
    "ln",
    "lt",
    "lv",
    "mai",
    "mg",
    "mi",
    "mk",
    "ml",
    "mn",
    "mr",
    "ms",
    "mt",
    "my",
    "nb",
    "ne",
    "nl",
    "oc",
    "om",
    "pa",
    "pag",
    "pam",
    "pl",
    "prs",
    "ps",
    "pt",
    "qu",
    "ro",
    "ru",
    "sa",
    "scn",
    "sk",
    "sl",
    "sq",
    "sr",
    "st",
    "su",
    "sv",
    "sw",
    "ta",
    "te",
    "tg",
    "tk",
    "tl",
    "tn",
    "tr",
    "ts",
    "tt",
    "uk",
    "ur",
    "uz",
    "vi",
    "wo",
    "xh",
    "yi",
    "yue",
    "zh",
    "zu",
}

TO_LANGS: Final[set[str]] = FR_LANGS | {
    "de-CH",
    "en-GB",
    "en-US",
    "es-419",
    "fr-CA",
    "pt-BR",
    "pt-PT",
    "zh-Hans",
    "zh-Hant",
} - {
    "auto",
    "en",
    "pt",
    "zh",
}
