FROM pandoc/latex:latest

RUN apk add --no-cache ttf-liberation font-liberation \
    && tlmgr update --self --force \
    && tlmgr install enumitem titlesec
