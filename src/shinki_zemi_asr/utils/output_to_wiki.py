# src/shinki_zemi_asr/utils/output_to_wiki.py

import os
import re
import requests
from dotenv import load_dotenv

# .env から環境変数をロード
load_dotenv()

# 環境変数の取得
BASE_URL = os.getenv("BASE_URL")
COLLECTION_ID = os.getenv("ZEMI_ASR_COLLECTION_ID")
API_TOKEN     = os.getenv("OUTLINE_API_TOKEN")

def get_title(filename: str) -> str:
    """
    :param filename: ファイル名 (例: "kazuma_20250427_1200_1300.json")
    :return: タイトル (例: "20250427_kazuma")
    """
    pattern = re.compile(
        r'^(?P<username>[^_]+)_'      # ユーザ名 (アンダースコア以外)
        r'(?P<date>\d{8})_'           # 日付 (YYYYMMDD)
        r'(?P<start>\d{4})_'          # 開始時刻 (HHMM)
        r'(?P<end>\d{4})\.json$'      # 終了時刻 (HHMM) + .json
    )
    m = pattern.match(filename)
    if not m:
        raise ValueError(f"無効なファイル名形式: {filename}")

    date = m.group('date')
    username = m.group('username')
    return f"{date}_{username}"

def output_to_wiki(text: str, filename: str) -> dict:
    """
    Outline API を呼び出してドキュメントを作成します。

    :param title: ドキュメントのタイトル
    :param text: 本文テキスト
    :param publish: 公開フラグ (True/False)
    :return: API のレスポンス JSON を辞書で返す
    """
    url = f"{BASE_URL}/documents.create"
    payload = {
        "title":        get_title(filename),  # タイトル
        "text":         text,
        "collectionId": COLLECTION_ID,
        "publish":      True
    }
    headers = {
        "Content-Type":  "application/json",
        "Authorization": f"Bearer {API_TOKEN}"
    }

    resp = requests.post(url, json=payload, headers=headers)
    # ステータスコード 200 異常時は例外を投げる
    resp.raise_for_status()
    return resp.json()
