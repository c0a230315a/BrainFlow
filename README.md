# BrainFlow / Neurosity Crown 計測スクリプト

このリポジトリは、BrainFlow を使って **Neurosity Crown** のストリーミングを開始し、停止時にローデータ（TSV）とメタデータ（JSON）を保存するための簡易スクリプトを置いています。

## 前提

- Windows（`keyboard` ライブラリのホットキー入力を使っています）
- Neurosity Crown 本体が利用可能で、BrainFlow から接続できる状態
- Python（このリポジトリには `setup.bat` で作れるポータブル Python 環境も用意しています）

## セットアップ

### 1) ポータブル Python を用意する（推奨）

1. `setup.bat` を実行（ポータブル Python をダウンロードし、pip をセットアップして VS Code を起動します）
   - 既存の `python-portable/` がある場合、再作成のために削除されます
2. VS Code のターミナルで必要なパッケージを入れます

```powershell
python -m pip install --upgrade pip
python -m pip install brainflow keyboard
```

> すでに `python-portable/` があり、`brainflow` / `keyboard` が入っている場合はインストール不要です。
> VS Code を起動せずに実行したい場合は `python-portable\\python.exe` を使ってください。

### 2) 既存の Python を使う（任意）

```powershell
python -m pip install brainflow keyboard
```

## `crown_brainflow_test.py` の使い方

```powershell
python crown_brainflow_test.py
```

ポータブル Python を使う場合:

```powershell
python-portable\python.exe crown_brainflow_test.py
```

実行すると Crown への接続（`prepare_session()`）→ ストリーミング開始（`start_stream()`）を行い、キー入力で操作します。

- `l` : `liar_timestamp` を記録（`time.time()` の epoch 秒）
- `s` : 計測を停止してファイル保存（ストリーム停止→セッション解放→書き出し）

### 保存先

スクリプト先頭の `experiment_name`（デフォルト `test1`）を使って、以下に保存します。

- ローデータ: `data/<experiment_name>/crown_raw/crown_raw_<YYYY-MM-DD_HH-MM-SS>.csv`
- メタデータ: `data/<experiment_name>/<experiment_name>_<YYYY-MM-DD_HH-MM-SS>.json`

メタデータ JSON には、保存した CSV 名と `liar_timestamp` の有無が入ります。

### ローデータ（CSV/TSV）について

`DataFilter.write_file(data, ...)` を使って保存しています。

- ファイルは **タブ区切り（TSV）**
- `get_board_data()` の戻り（channels x samples）を **ファイルでは転置（samples x channels）** して書き出します

Python で読み戻す例:

```python
from brainflow.data_filter import DataFilter

data = DataFilter.read_file("data/test1/crown_raw/crown_raw_YYYY-MM-DD_HH-MM-SS.csv")
print(data.shape)  # (channels, samples) (get_board_data() と同じ向き)
```

TSV をそのまま（ファイル上の向きのまま）読みたい場合は、例えば pandas でタブ区切りとして読めます。

```python
import pandas as pd

df = pd.read_csv(
    "data/test1/crown_raw/crown_raw_YYYY-MM-DD_HH-MM-SS.csv",
    sep="\t",
    header=None,
)
print(df.shape)  # (samples, channels) 相当
```

## カスタマイズ

- 実験名を変えたい場合: `crown_brainflow_test.py` 内の `experiment_name = "..."` を変更してください。

## トラブルシュート

- `prepare_session()` で失敗する: Crown の状態（電源/接続）を確認し、再実行してください。例外時にも `release_session()` するようにはしてあります。
- キー入力が反応しない: `keyboard` のホットキーを使っているため、環境によっては権限やセキュリティソフト設定の影響を受けることがあります。
