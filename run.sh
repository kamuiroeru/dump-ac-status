#!/bin/bash

# 定期実行用スクリプト

cd $(dirname $0)  # このスクリプトのディレクトリに移動

source .venv/bin/activate

# 80文字数の線を書く
echo -n "# "
for _ in `seq 1 39`; do
    echo -n "--"  # "-" だと表示されなかった
done
echo 
date

# 読み込む
python update_sega_log.py
python notify.py
