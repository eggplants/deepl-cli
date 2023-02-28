FROM mcr.microsoft.com/playwright/python:v1.31.1-focal

RUN pip3 install -U --progress-bar=off --no-use-pep517 deepl-cli

ENTRYPOINT ["deepl"]
