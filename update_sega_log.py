# maimai と ongeki の現在のカウントを log に 保存する。

from typing import Final, List, NamedTuple
from os.path import abspath, dirname, join as pjoin
SCRIPT_DIR: Final[str] = abspath(dirname(__file__))

from credentials.create_cred import Cred
cred = Cred('sega').load()

import chromedriver_binary  # パスの読み込みに必須
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.webdriver import WebDriver
import json
from string import Template
from urllib.request import Request, urlopen
from itertools import product
from collections import defaultdict


def maimai(driver: WebDriver) -> int:
    """maimai のプレイ回数を取得"""

    # maimai NET にログイン
    print('login now ...')
    driver.get('https://maimaidx.jp/maimai-mobile/')
    id_elem: WebElement = driver.find_element_by_name('segaId')
    id_elem.clear()
    id_elem.send_keys(cred.ID)
    pass_elem: WebElement = driver.find_element_by_name('password')
    pass_elem.clear()
    pass_elem.send_keys(cred.PASS)
    id_elem.submit()

    # プレイヤーデータページへ遷移
    print('get play count ...')
    driver.find_element_by_name('idx').submit()
    driver.get('https://maimaidx.jp/maimai-mobile/playerData/')

    # プレイ回数が書かれているエレメントを取得
    play_count_div: WebElement = driver.find_element_by_xpath('//div[contains(text(), "プレイ回数")]')
    play_count = play_count_div.text.split('：')[1][:-1]

    return int(play_count)


def ongeki(driver: WebDriver) -> int:
    """オンゲキ のプレイ回数を取得"""

    # オンゲキ NET にログイン
    print('login now ...')
    driver.get('https://ongeki-net.com/ongeki-mobile/')
    id_elem: WebElement = driver.find_element_by_name('segaId')
    id_elem.clear()
    id_elem.send_keys(cred.ID)
    pass_elem: WebElement = driver.find_element_by_name('password')
    pass_elem.clear()
    pass_elem.send_keys(cred.PASS)
    id_elem.submit()

    # プレイヤーデータページへ遷移
    print('get play count ...')
    driver.find_element_by_name('idx').submit()
    driver.get('https://ongeki-net.com/ongeki-mobile/home/playerDataDetail/')

    # プレイトラック数が書かれているエレメントを取得して一番うしろを取る
    user_detail_element: WebElement = driver.find_element_by_css_selector('.user_data_detail_block')
    total_play_track_count = user_detail_element.text.split(' ')[-1]

    return int(total_play_track_count)


LOG_JSON_PATH: Final[str] = pjoin(SCRIPT_DIR, 'logs', 'sega.json')


class LogElement(NamedTuple):
    date_iso_str: str
    maimai: int
    ongeki: int


def save_log(logs: List[LogElement]):
    """log を json 形式で保存する"""
    logs_for_json = [log._asdict() for log in logs]
    json.dump(logs_for_json, open(LOG_JSON_PATH, 'w'), indent=2)  # 整形して出力


def load_log() -> List[LogElement]:
    """log を読み込む"""
    loaded: List[dict] = []
    try:
        loaded = json.load(open(LOG_JSON_PATH))
    except FileNotFoundError:
        pass

    return [LogElement(**log) for log in loaded]


def calc_ongeki_credit(track_count: int) -> List[int]:
    """プレイ曲数からクレジットを計算する
    〜考え方〜
    1. 3a + 5b = c において、 c が track_count 以上かつ最小である (a, b) の組を求める
    2. この (a, b) に対して、a + 2b がクレジット回数になる。
    3. ただし、(a, b) の組が複数現れることもある。
    """
    c2ab = defaultdict(list)
    for a, b in product(range(20), range(20)):
        c = 3*a + 5*b
        c2ab[c].append((a, b))
    search_list = sorted(c2ab.keys())
    i = 0
    while search_list[i] < track_count:
        i += 1

    ab_list = c2ab[search_list[i]]
    return [a + 2 * b for a, b in ab_list]


def notify():
    """logsの後ろ2つを取って、maimai と ongeki の数値が違ったら通知する。"""
    slack_cred = Cred('slack')
    webhook_url = slack_cred.load().PASS

    message_tpl = '''SEGA 音ゲープレイ履歴
    maimai: $maimai_prev -> $maimai_now ($maimai_credit クレジット)
    ongeki: $ongeki_prev -> $ongeki_now ($ongeki_credit クレジット)
    '''
    tpl = Template(message_tpl)

    logs = load_log()
    prev, now = logs[-2:]
    if prev.maimai != now.maimai or prev.ongeki != now.ongeki:
        maimai_credit = now.maimai - prev.maimai
        ongeki_credit = calc_ongeki_credit(now.ongeki - prev.ongeki)
        message = tpl.substitute(
            maimai_prev=prev.maimai,
            ongeki_prev=prev.ongeki,
            maimai_now=now.maimai,
            ongeki_now=now.ongeki,
            maimai_credit=maimai_credit,
            ongeki_credit=ongeki_credit,
        )
        # POST する
        req = Request(
            webhook_url,
            json.dumps({'text': message}).encode(),
            {'Content-Type': 'application/json'}
        )
        with urlopen(req) as res:
            body = res.read()
            print(body)


if __name__ == '__main__':
    from datetime import datetime
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)

    print('get maimai count ...')
    maimai_count = maimai(driver)
    print('get ongeki count ...')
    ongeki_count = ongeki(driver)
    driver.quit()
    now_string = datetime.now().isoformat()
    le = LogElement(now_string, maimai_count, ongeki_count)

    logs = load_log()
    logs.append(le)
    save_log(logs)