#!/usr/bin/env python3.8
import asyncio

from . import deepl


def main():
    t = deepl.DeepLCLI()
    t.validate()
    if len(t.scripts) > 0:
        print(asyncio.get_event_loop().run_until_complete(t.translate()))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
