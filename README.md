# 新規ゼミASRプロジェクト
## インストール方法
リポジトリーをクローン
```
git clone https://github.com/oukoutdam/shinki_zemi_asr.git
cd shinki_zemi_asr
```
必要なパッケージのインストール
```
poetry install
```
Pythonの仮想環境を使用する
```
eval $(poetry env activate)
```
開発用ウェブサーバを実行する（コード更新したら、すぐに反映する）
```
fastapi dev src/shinki_zemi_asr/main.py
```
デプロイ用サーバを実行する
```
fastapi run src/shinki_zemi_asr/main.py
```
## その他
新しいパッケージの追加
```
poetry add <package-name>
```


