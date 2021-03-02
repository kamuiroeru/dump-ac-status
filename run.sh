#!/bin/bash

# 定期実行用スクリプト
source .venv/bin/activate

python update_sega_log.py
python notify.py