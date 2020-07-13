#!/usr/bin/env python3.8
from . import deepl

def main():
    t = deepl.DeepLCLI()
    t.validate()
    print(t.translate())

if __name__ == '__main__':
    main()
