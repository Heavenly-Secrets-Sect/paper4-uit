#!/bin/bash
# Runs the eight ext_tlp2 evaluation configs sequentially (pre-registered order, docs/ext/tlp2.md section 4).
cd "$(dirname "$0")/../../.."
for tag in "$@"; do
  echo "=== $tag start $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  python3 experiments/ext/tlp2/run_cells.py --config experiments/configs/ext_tlp2_$tag.json --workers 3 2>&1 | grep -v -i "warning\|return _core" 
  echo "=== $tag end $(date -u +%Y-%m-%dT%H:%M:%SZ)"
done
