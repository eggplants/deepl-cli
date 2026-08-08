FROM mcr.microsoft.com/playwright/python:v1.55.0-noble@sha256:640d578aae63cfb632461d1b0aecb01414e4e020864ac3dd45a868dc0eff3078

ARG VERSION
ENV VERSION ${VERSION:-master}

RUN python -m pip install git+https://github.com/eggplants/deepl-cli@${VERSION}

ENTRYPOINT ["deepl"]
