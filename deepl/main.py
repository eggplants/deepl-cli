#!/usr/bin/env python3
import sys

from . import deepl


def main() -> None:
    t = deepl.DeepLCLI()
    t.chk_cmdargs()
    t.fr_lang, t.to_lang = sys.argv[1].split(':')
    script = sys.stdin.read()
    print('Translating...', end='', file=sys.stderr, flush=True)
    result = t.translate(script)
    print('\033[1K\033[G', end='', file=sys.stderr, flush=True)
    print(result)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
