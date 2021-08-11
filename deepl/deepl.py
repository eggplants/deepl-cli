import sys
import urllib.request
from textwrap import dedent
from typing import Tuple

from translatepy import Translator  # type: ignore


class DeepLCLIArgCheckingError(Exception):
    pass


class DeepLCLITranslationFailure(Exception):
    pass


class DeepLCLI:

    def __init__(self) -> None:
        self.max_length = 5000

    def usage(self) -> None:
        """Print usage."""

        print(dedent('''\
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
            $ deepl en:ru <<'EOS' # :ru is equivalent of auto:ru
              good morning!
              good night.
              EOS
            $ deepl fr:zh <<<"Mademoiselle"
            $ deepl de:pl < README_de.md
        LANGUAGE CODES:
            <from:lang>: {auto it et nl el sv es sk sl cs da
                          de hu fi fr bg pl pt lv lt ro ru en zh ja}
            <to:lang>:   {it et nl el sv es sk sl cs da
                          de hu fi fr bg pl pt lv lt ro ru en zh ja}
        '''))

    def internet_on(self) -> bool:
        """Check an internet connection."""
        try:
            urllib.request.urlopen('https://www.google.com/', timeout=10)
            return True
        except IOError:
            return False

    def _chk_stdin(self) -> None:
        """Check if stdin is entered."""
        if (sys.stdin.isatty() and len(sys.argv) == 1) or '-h' in sys.argv:
            # if `$ deepl` or `$ deepl -h`
            self.usage()
            sys.tracebacklimit = 0
            raise DeepLCLIArgCheckingError('show help.')
        elif sys.stdin.isatty():
            # raise err if stdin is empty
            raise DeepLCLIArgCheckingError('stdin seems to be empty.')

    def _chk_lang(self, in_lang: Tuple[str, str]) -> Tuple[str, str]:
        """Check if language options are valid."""
        fr_langs = {'auto', 'it', 'et', 'nl', 'el',
                    'sv', 'es', 'sk', 'sl', 'cs',
                    'da', 'de', 'hu', 'fi', 'fr',
                    'bg', 'pl', 'pt', 'lv', 'lt',
                    'ro', 'ru', 'en', 'zh', 'ja', ''}
        to_langs = fr_langs - {'auto', ''}

        if len(in_lang) != 2:
            # raise err if langs is not (str, str)
            raise DeepLCLIArgCheckingError('correct your lang format.')
        else:
            in_fr_lang, in_to_lang = in_lang

        if in_fr_lang not in fr_langs:
            raise DeepLCLIArgCheckingError('invalid fr_lang: ' + in_fr_lang)
        elif in_to_lang not in to_langs:
            raise DeepLCLIArgCheckingError('invalid to_lang: ' + in_to_lang)

        if in_fr_lang == in_to_lang:
            # raise err if <fr:lang> == <to:lang>
            raise DeepLCLIArgCheckingError('two languages cannot be same.')

        return (in_fr_lang.replace('auto', ''), in_to_lang)

    def chk_cmdargs(self) -> None:
        """Check cmdargs and configurate languages.(for using as a command)"""
        self._chk_stdin()

    def _chk_script(self, script: str) -> str:
        """Check cmdarg and stdin."""

        script = script.rstrip()

        if self.max_length is not None and len(script) > self.max_length:
            raise DeepLCLIArgCheckingError(
                'limit of script is less than {} chars(Now: {} chars).'.format(
                    self.max_length, len(script)))
        if len(script) <= 0:
            raise DeepLCLIArgCheckingError('script seems to be empty.')

        return script

    def translate(self, script: str, fr_lang: str, to_lang: str) -> str:
        self.fr_lang, self.to_lang = self._chk_lang((fr_lang, to_lang))
        self._chk_script(script)
        t = Translator().deepl_translate
        res = t.translate(script, self.to_lang, self.fr_lang)
        if res == (None, None):
            raise DeepLCLITranslationFailure
        else:
            return res[1]