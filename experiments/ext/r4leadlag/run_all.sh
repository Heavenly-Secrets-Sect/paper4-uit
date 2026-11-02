#!/bin/bash
# Evaluation runs of r4leadlag (after drive.py calibrate). Logs in experiments/ext/r4leadlag/logs/.
cd /Users/kietnt/Desktop/Workspace/Paper4_UIT
PY=/Users/kietnt/miniconda3/bin/python
L=experiments/ext/r4leadlag/logs
for c in latent clean noise; do
  echo "start $c $(date -u +%H:%M:%SZ)" >> $L/timeline.txt
  $PY experiments/ext/r4leadlag/drive.py run --config experiments/configs/ext_r4leadlag_eval_$c.json --workers 3 > $L/run_$c.log 2>&1
  echo "end $c $(date -u +%H:%M:%SZ) exit $?" >> $L/timeline.txt
done
echo "ALLDONE" >> $L/timeline.txt
