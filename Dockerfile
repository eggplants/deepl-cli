FROM mcr.microsoft.com/playwright/python:v1.32.1-focal

ARG VERSION
ENV VERSION ${VERSION:-master}

RUN python -m pip install git+https://github.com/eggplants/deepl-cli@${VERSION}

ENTRYPOINT ["deepl"]
