#!/bin/sh
# Export the resume PDF from resume.tex using the pre-built resume-latex image.
# Build the image first:  docker build -t resume-latex .

set -e

IMAGE=resume-latex
DIR="$(cd "$(dirname "$0")" && pwd)"

docker run --rm \
  -v "$DIR":/data \
  --entrypoint sh \
  "$IMAGE" -c "
    xelatex -output-directory=/data /data/resume.tex
    xelatex -output-directory=/data /data/resume.tex
    mv /data/resume.pdf '/data/Mohammad Alif Yasir bin Soleh Resume.pdf'
    rm -f /data/resume.aux /data/resume.log /data/resume.out
  "
