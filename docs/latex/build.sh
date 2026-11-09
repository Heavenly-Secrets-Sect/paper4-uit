#!/usr/bin/env bash
# Biên dịch main.pdf bằng XeLaTeX + BibTeX. Chạy từ thư mục docs/latex:  bash build.sh
set -euo pipefail
cd "$(dirname "$0")"
xelatex -interaction=nonstopmode -halt-on-error main.tex >/dev/null
bibtex main >/dev/null || true
xelatex -interaction=nonstopmode -halt-on-error main.tex >/dev/null
xelatex -interaction=nonstopmode -halt-on-error main.tex
echo "OK: $(pwd)/main.pdf"
