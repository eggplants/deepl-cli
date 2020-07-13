from .deepl import DeepLCLI

def main():
    t = DeepLCLI()
    t.validate()
    print(t.translate())

if __name__ == '__main__':
    main()
