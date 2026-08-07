# Resume

`resume.tex` is the single source of truth. The PDF and `index.html` are generated from it.

## Generate the PDF

```bash
docker run --rm \
  -v "$(pwd)":/data \
  --entrypoint sh \
  pandoc/latex:latest -c "
    apk add --no-cache ttf-liberation font-liberation 2>/dev/null
    tlmgr update --self --force 2>/dev/null
    tlmgr install enumitem titlesec 2>/dev/null
    xelatex -output-directory=/data /data/resume.tex
    mv /data/resume.pdf '/data/Mohammad Alif Yasir bin Soleh Resume.pdf'
    rm -f /data/resume.aux /data/resume.log /data/resume.out
  "
```

## Generate the HTML

```bash
python3 generate_html.py
```

The script converts `resume.tex` with pandoc (via the same `pandoc/latex:latest`
Docker image, or a local `pandoc` binary if one is installed) and post-processes
the output into `index.html`. Requires a local `python3`; Docker is used when
`pandoc` is not on `PATH`.