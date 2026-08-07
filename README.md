# Resume

`resume.tex` is the single source of truth. The PDF and `index.html` are generated from it.

## Export the PDF

The LaTeX image with all dependencies is built once, then the PDF is exported with a single command.

```bash
# 1. Create the image with dependencies (fonts, enumitem, titlesec)
docker build -t resume-latex .

# 2. Export the PDF
./export_pdf.sh
```

`export_pdf.sh` runs two xelatex passes inside `resume-latex`, writes
`Mohammad Alif Yasir bin Soleh Resume.pdf`, and cleans up auxiliary files.

## Generate the HTML

```bash
python3 generate_html.py
```

The script converts `resume.tex` with pandoc (via the `pandoc/latex:latest`
Docker image, or a local `pandoc` binary if one is installed) and post-processes
the output into `index.html`. Requires a local `python3`; Docker is used when
`pandoc` is not on `PATH`.