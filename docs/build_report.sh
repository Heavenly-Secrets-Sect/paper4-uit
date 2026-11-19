#!/usr/bin/env bash
# Biên dịch báo cáo phản hồi bằng XeLaTeX. Chạy: bash docs/build_report.sh
set -euo pipefail
cd "$(dirname "$0")"
python3 make_report_tables.py
xelatex -interaction=nonstopmode -halt-on-error bao_cao_phan_hoi_thay_2026-11-15.tex >/dev/null
xelatex -interaction=nonstopmode -halt-on-error bao_cao_phan_hoi_thay_2026-11-15.tex | tail -3
