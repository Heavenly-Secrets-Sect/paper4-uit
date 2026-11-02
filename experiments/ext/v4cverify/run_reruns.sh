#!/bin/bash
# R3-7: two reruns of 2 units of ext_v4c_eval with --workers 3 (miniconda, then CLT python3), sequential.
cd /Users/kietnt/Desktop/Workspace/Paper4_UIT
date -u +%FT%TZ > experiments/ext/v4cverify/rerun_start.txt
python -c "import sys,numpy,scipy;print(sys.executable,numpy.__version__,scipy.__version__)" > experiments/ext/v4cverify/rerun_w3_env.txt
python experiments/run_experiment.py --config experiments/configs/ext_v4cverify_rerun_w3.json --workers 3 > experiments/ext/v4cverify/rerun_w3.log 2>&1
date -u +%FT%TZ >> experiments/ext/v4cverify/rerun_start.txt
/Library/Developer/CommandLineTools/usr/bin/python3 -c "import sys,numpy,scipy;print(sys.executable,numpy.__version__,scipy.__version__)" > experiments/ext/v4cverify/rerun_w3_clt_env.txt
/Library/Developer/CommandLineTools/usr/bin/python3 experiments/run_experiment.py --config experiments/configs/ext_v4cverify_rerun_w3_clt.json --workers 3 > experiments/ext/v4cverify/rerun_w3_clt.log 2>&1
date -u +%FT%TZ >> experiments/ext/v4cverify/rerun_start.txt
