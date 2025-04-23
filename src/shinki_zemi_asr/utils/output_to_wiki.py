# src/shinki_zemi_asr/utils/output_to_wiki.py

import os
import requests
from dotenv import load_dotenv

# .env から環境変数をロード
load_dotenv()

# config.py に定義があればそちらを使うか、ここでデフォルト値を定義
BASE_URL = os.getenv("BASE_URL", "http://133.15.57.8/api")
COLLECTION_ID = os.getenv("ZEMI_ASR_COLLECTION_ID")
API_TOKEN     = os.getenv("OUTLINE_API_TOKEN")

def get_title() -> str:
    """
    :param filename: ファイル名 (例: "kazuma_20250427_1200_1300.json")
    :return: タイトル (例: "20250427_kazuma")
    """
    #src/shinki_zemi_asr/Transcriptionからfilenameを取得する
    # ここでは例として、ファイル名を直接指定しています。
    filename = "kazuma_20250427_1200_1300.json"  
    # 例: "kazuma_20250427_1200_1300.json"
    # ファイル名から日付と名前を抽出    
    # 例: "kazuma_20250427_1200_1300.json" -> "20250427_kazuma"
    name, date = filename.split("_")[:2]
    return f"{name}_{date}"


def output_to_wiki(title: str, text: str, publish: bool = True) -> dict:
    """
    Outline API を呼び出してドキュメントを作成します。

    :param title: ドキュメントのタイトル
    :param text: 本文テキスト
    :param publish: 公開フラグ (True/False)
    :return: API のレスポンス JSON を辞書で返す
    """
    url = f"{BASE_URL}/documents.create"
    payload = {
        "title":        get_title(),
        "text":         text,
        "collectionId": COLLECTION_ID,
        "publish":      publish
    }
    headers = {
        "Content-Type":  "application/json",
        "Authorization": f"Bearer {API_TOKEN}"
    }

    resp = requests.post(url, json=payload, headers=headers)
    # ステータスコード 200 異常時は例外を投げる
    resp.raise_for_status()
    return resp.json()
