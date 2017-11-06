#!/usr/bin/env bash
cd "$(dirname "$0")"
sleep 10
source ./.venv/bin/activate
python ./main.py >> logit.txt 2>&1
