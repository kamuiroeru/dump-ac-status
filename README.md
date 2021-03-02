# Dump Ac Status
アーケードゲーム（maimai と オンゲキ から対応）のプレイ回数とかを、selenium を使って記録していきたい。

## Requirements
- python3.8 >=

## Install

Install dependencies.
```shell
$ ./install.sh
```

Add credentials
```shell
$ source .venv/bin/activate
$ python credentials/create_cred.py sega  # maimai と ongeki のデータを取得するため
$ python credentials/create_cred.py slack  # slack に通知する場合は PASS に webhook URL を登録する
```

## Enable cron
[run.sh](run.sh) を crontab に登録したらOK