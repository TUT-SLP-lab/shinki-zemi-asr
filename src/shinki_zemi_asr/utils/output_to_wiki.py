# src/shinki_zemi_asr/utils/output_to_wiki.py

import os
import requests
from dotenv import load_dotenv

# .env から環境変数をロード
load_dotenv()

# 環境変数の取得
BASE_URL = os.getenv("BASE_URL")
COLLECTION_ID = os.getenv("ZEMI_ASR_COLLECTION_ID")
API_TOKEN     = os.getenv("OUTLINE_API_TOKEN")

import re
from pathlib import Path
from datetime import datetime

def get_latest_transcription_info():
    """
    Transcription フォルダ内のファイル名規則:
      {username}_{YYYYMMDD}_{HHMM}_{HHMM}.json
    にマッチするファイルを検索し、
    日付 + 開始時刻 が最も新しいファイルの
    (ユーザ名, 日付 (YYYYMMDD), ファイル名) を返す。
    """
    # Transcription ディレクトリへのパスを取得
    transcription_dir = Path(__file__).resolve().parent.parent / 'Transcription'

    # ファイル名パターン
    pattern = re.compile(
        r'^(?P<username>[^_]+)_'      # ユーザ名 (アンダースコア以外)
        r'(?P<date>\d{8})_'           # 日付 (YYYYMMDD)
        r'(?P<start>\d{4})_'          # 開始時刻 (HHMM)
        r'(?P<end>\d{4})\.json$'      # 終了時刻 (HHMM) + .json
    )

    latest_dt = None
    latest_info = None

    for file in transcription_dir.iterdir():
        if file.suffix.lower() != '.json':
            continue
        m = pattern.match(file.name)
        if not m:
            continue

        # 比較用の datetime を作成 (日付＋開始時刻)
        dt = datetime.strptime(m.group('date') + m.group('start'), '%Y%m%d%H%M')

        if latest_dt is None or dt > latest_dt:
            latest_dt = dt
            latest_info = {
                'username': m.group('username'),
                'date': m.group('date'),
                'filename': file.name
            }

    if latest_info is None:
        raise FileNotFoundError(f"No matching JSON files in {transcription_dir}")

    return latest_info

def get_title() -> str:
    """
    :param filename: ファイル名 (例: "kazuma_20250427_1200_1300.json")
    :return: タイトル (例: "20250427_kazuma")
    """
    # src/shinki_zemi_asr/Transcriptionからfilename,dateを取得する
    info = get_latest_transcription_info() 
    return f"{info['date']}_{info['username']}"


def output_to_wiki(text: str) -> dict:
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
