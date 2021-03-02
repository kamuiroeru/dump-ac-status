from typing import Final, NamedTuple, Optional
from string import Template
import base64
import json
from os.path import dirname, abspath, exists, join as pjoin

SCRIPT_DIR = abspath(dirname(__file__))
BASE_TPL = Template(open(pjoin(SCRIPT_DIR, 'template.json')).read())

USAGE: Final[str] = 'usage: python3 create_cred.py template\nexample: python3 create_cred.py sega'


class Cred:
    """IDとPASSのJSON文字列をbase64で扱うクラス"""

    CCS = 'utf-8'  # Coded Caracter Set つまり文字コード

    class IdPass(NamedTuple):
        ID: str
        PASS: str

    def __init__(self, label: str) -> None:
        self.label = label
        self.cred_file_path = pjoin(SCRIPT_DIR, f'{label}.cred')

    @classmethod
    def b64encode(cls, s: str) -> str:
        b = s.encode(cls.CCS)
        return base64.b64encode(b).decode(cls.CCS)

    @classmethod
    def b64decode(cls, s: str) -> str:
        b = s.encode(cls.CCS)
        return base64.b64decode(b).decode(cls.CCS)

    def save(self):
        """IDとPASSをセーブする"""
        # 上書き確認
        if exists(self.cred_file_path):
            y_or_n = input(f'{self.label}.cred is already exists. Do you want update this ? y/[n]: ')
            if y_or_n != 'y':
                print('skiped...')
                return

        # 保存する
        _id = input('ID: ')
        _pass = input('PASS: ')
        filled_json = BASE_TPL.substitute(ID=_id, PASS=_pass)
        open(self.cred_file_path, 'w').write(self.b64encode(filled_json))

    def load(self) -> Optional['IdPass']:
        """IDとPASSを読み込む"""
        encoded: str
        try:
            encoded = open(self.cred_file_path).read()
        except FileNotFoundError:
            return None

        decoded_json = self.b64decode(encoded)
        decoded: dict = json.loads(decoded_json)
        return self.IdPass(**decoded)


if __name__ == '__main__':
    from sys import argv
    if len(argv) <= 1:
        print(USAGE)
        exit(1)
    cred = Cred(argv[1])
    cred.save()
    print('saved')
