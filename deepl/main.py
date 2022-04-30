from __future__ import annotations

import argparse
import os
import sys
import warnings
from shutil import get_terminal_size
from typing import cast

from deepl import __version__

from .deepl import DeepLCLI

warnings.filterwarnings("ignore")


class DeepLCLIFormatter(
    argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter
):
    pass


def check_file(v: str) -> str:
    def is_binary_string(b: bytes) -> bool:
        return bool(b.translate(None, textchars))

    textchars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7F})
    if not os.path.isfile(v):
        raise argparse.ArgumentTypeError(f"{repr(v)} is not file.")
    elif not is_binary_string(cast(bytes, open(v, "rb"))):
        raise argparse.ArgumentTypeError(f"{repr(v)} is not text file.")
    else:
        return v


def check_input_lang(lang: str) -> str:
    if lang not in DeepLCLI.fr_langs:
        raise argparse.ArgumentTypeError(
            f"{repr(lang)} is not valid language. Valid language:\n"
            + repr(DeepLCLI.fr_langs)
        )
    else:
        return lang


def check_output_lang(lang: str) -> str:
    if lang not in DeepLCLI.to_langs:
        raise argparse.ArgumentTypeError(
            f"{repr(lang)} is not valid language. Valid language:\n"
            + repr(DeepLCLI.to_langs)
        )
    else:
        return lang


def parse_args(test: str | None = None) -> argparse.Namespace:
    """Parse arguments."""
    parser = argparse.ArgumentParser(
        prog="deepl",
        formatter_class=(
            lambda prog: DeepLCLIFormatter(
                prog,
                **{
                    "width": get_terminal_size(fallback=(120, 50)).columns,
                    "max_help_position": 25,
                },
            )
        ),
        description="DeepL Translator CLI without API Key",
        epilog=(
            "valid languages of `--fr`:\n"
            + repr(DeepLCLI.fr_langs)
            + "\n\nvalid languages of `--to`:\n"
            + repr(DeepLCLI.to_langs)
        ),
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-f",
        "--file",
        metavar="PATH",
        type=check_file,
        help="source text file to translate",
    )
    group.add_argument(
        "-s",
        "--stdin",
        action="store_true",
        help="read source text from stdin",
    )
    parser.add_argument(
        "--fr", type=check_input_lang, help="input language", default="auto"
    )
    parser.add_argument(
        "--to", type=check_output_lang, help="output language", required=True
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {__version__}"
    )

    if test is None:
        return parser.parse_args()
    else:
        return parser.parse_args(test)


def main(test: str | None = None) -> None:
    args = parse_args(test)
    t = DeepLCLI(args.fr, args.to)
    script = ""
    if args.stdin:
        if sys.stdin is None:
            raise OSError("stdin is empty.")
        else:
            script = "\n".join(sys.stdin.readlines()).rstrip("\n")
    else:
        script = open(args.file, "r").read().rstrip("\n")

    print("Translating...", end="", file=sys.stderr, flush=True)
    res = t.translate(script)
    print("\033[1K\033[G", end="", file=sys.stderr, flush=True)
    print(res)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
