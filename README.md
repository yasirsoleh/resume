# Resume

Generate the PDF using Docker:

```bash
docker run --rm \
  -v "$(pwd)":/data \
  --entrypoint sh \
  pandoc/latex:latest -c "
    apk add --no-cache ttf-liberation font-liberation 2>/dev/null
    tlmgr update --self --force 2>/dev/null
    tlmgr install enumitem titlesec 2>/dev/null
    xelatex -output-directory=/data /data/resume.tex
    rm -f /data/resume.aux /data/resume.log /data/resume.out
  "
```
