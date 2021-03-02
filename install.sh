#!/bin/bash

# python の 仮想環境を作り、selenium と chrome-driver をインストール する

## 仮想環境を作る
python -m venv .venv
source .venv/bin/activate

## selenium のインストール
pip install selenium

## 使っている Chrome のバージョンに合った chrome-driver をインストール
### OS ごとに インストールされている chrome のメジャーバージョンを取得
# OSごとの条件分岐はこれを参考にした https://qiita.com/UmedaTakefumi/items/fe02d17264de6c78443d
if [ "$(uname)" == 'Darwin' ]; then
    # Mac
    MAJ_VAR_S=$("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --version)
elif [ "$(expr substr $(uname -s) 1 5)" == 'Linux' ]; then
    # Linux
    MAJ_VAR_S=$(google-chrome --version)
else
    echo "Your platform ($(uname -a)) is not supported."
    exit 1
fi
MAJ_VAR=$(echo $MAJ_VAR_S | cut -d" " -f 3 | cut -d"." -f 1)
echo 'Chrome major version is' $MAJ_VAR

### pip でインストール
pip install -U chromedriver-binary==$MAJ_VAR.*