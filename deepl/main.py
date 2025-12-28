"""Main module of deepl CLI."""

import argparse
import sys
import warnings
from pathlib import Path
from shutil import get_terminal_size

from deepl import __version__
from deepl.languages import FR_LANGS, TO_LANGS

from .deepl import DeepLCLI

warnings.filterwarnings("ignore")


class DeepLCLIFormatter(
    argparse.ArgumentDefaultsHelpFormatter,
    argparse.RawDescriptionHelpFormatter,
):
    """Custom help formatter for argparse."""


def check_file(v: str) -> str:
    """Check if the file is a text file.

    Args:
        v (str): file path
    Returns:
        str: file path
    Raises:
        argparse.ArgumentTypeError: if the file is not a text file
    """

    def is_binary_string(b: bytes) -> bool:
        chars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7F})
        return bool(b.translate(None, chars))

    path = Path(v)

    if not path.is_file():
        msg = f"{v!r} is not file."
        raise argparse.ArgumentTypeError(msg)
    if is_binary_string(path.open(mode="rb").read(1024)):
        msg = f"{v!r} is not text file."
        raise argparse.ArgumentTypeError(msg)

    return v


def check_natural(v: str) -> int:
    """Check if the value is a natural number.

    Args:
        v (str): value to check
    Returns:
        int: value
    Raises:
        argparse.ArgumentTypeError: if the value is not a natural number
    """
    n = int(v)
    if n < 0:
        msg = f"{v} must not be negative."
        raise argparse.ArgumentTypeError(msg)

    return n


def check_input_lang(lang: str) -> str:
    """Check if the input language is valid.

    Args:
        lang (str): input language
    Returns:
        str: input language
    Raises:
        argparse.ArgumentTypeError: if the input language is not valid
    """
    if lang not in FR_LANGS:
        raise argparse.ArgumentTypeError(
            f"{lang!r} is not valid language. Valid language:\n" + repr(FR_LANGS),
        )

    return lang


def check_output_lang(lang: str) -> str:
    """Check if the output language is valid.

    Args:
        lang (str): output language
    Returns:
        str: output language
    Raises:
        argparse.ArgumentTypeError: if the output language is not valid
    """
    if lang not in TO_LANGS:
        raise argparse.ArgumentTypeError(
            f"{lang!r} is not valid language. Valid language:\n" + repr(TO_LANGS),
        )
    return lang


def parse_args(test: str | None = None) -> argparse.Namespace:
    """Parse arguments.

    Args:
        test (str | None): test string
    Returns:
        argparse.Namespace: parsed arguments
    Raises:
        argparse.ArgumentTypeError: if the arguments are not valid
    """
    parser = argparse.ArgumentParser(
        prog="deepl",
        formatter_class=(
            lambda prog: DeepLCLIFormatter(
                prog,
                width=get_terminal_size(fallback=(120, 50)).columns,
                max_help_position=25,
            )
        ),
        description="DeepL Translator CLI without API Key",
        epilog=(
            "valid languages of `-F` / --fr`:\n"
            + repr(FR_LANGS)
            + "\n\nvalid languages of `-T` / `--to`:\n"
            + repr(TO_LANGS)
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
        "-F",
        "--fr",
        type=check_input_lang,
        help="input language",
        required=True,
    )
    parser.add_argument(
        "-T",
        "--to",
        type=check_output_lang,
        help="output language",
        required=True,
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=check_natural,
        help="timeout interval",
        metavar="MS",
        default=5000,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="make output verbose",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    if test is None:
        return parser.parse_args()
    return parser.parse_args(test)


def main(test: str | None = None) -> None:
    """Main function.

    Args:
        test (str | None): test string
    """
    args = parse_args(test)
    t = DeepLCLI(args.fr, args.to, timeout=args.timeout)
    script = ""
    if args.stdin:
        if sys.stdin is None:
            msg = "stdin is empty."
            raise OSError(msg)

        script = "\n".join(sys.stdin.readlines()).rstrip("\n")

    else:
        file_path = Path(args.file)
        script = file_path.open(mode="r").read().rstrip("\n")

    if args.verbose:
        print("Translating...", end="", file=sys.stderr, flush=True)

    res = t.translate(script)

    if args.verbose:
        print("\033[1K\033[G", end="", file=sys.stderr, flush=True)

    print(res)


if __name__ == "__main__":
    main()
