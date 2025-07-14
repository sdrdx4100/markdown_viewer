# Markdown Viewer

Windows向けMarkdownビューア・エディタ

## 概要
- 左ペインでMarkdownを編集し、右ペインでリアルタイムプレビュー
- PySide6 + QtWebEngineでGUIを実装
- `markdown`パッケージでMarkdown→HTML変換
- PyInstallerで単一のexe化
- Windowsのエクスプローラー右クリックメニューに登録可能
- 検索・置換や最近使ったファイル履歴、設定ダイアログを搭載
- 新規ファイル作成に対応
- プレビューのON/OFFや同期スクロールを備えた分割ビュー

## ファイル構成
```
markdown_viewer/
├── main.py                # メインアプリケーション
├── register_context_menu.py  # 右クリックメニュー登録・解除スクリプト
├── requirements.txt
├── README.md
├── module/                # アプリケーションロジック
│   ├── main_window.py
│   └── register_context_menu.py
└── static/                # アイコンやスタイルシート
    ├── icon.ico
    └── style.css
```

## 開発環境準備
```powershell
cd <project_root>
python -m venv .venv
.\.venv\Scripts\Activate
pip install -r requirements.txt
```

## ビルド
PyInstaller を利用して実行形式を作成できます（`--onefile` を指定しないため、高速起動が可能です）。
- 修正版コマンド例:
```powershell
pyinstaller --windowed --name MarkdownViewer --icon="static/icon.ico" main.py
```

## コンテキストメニュー登録
生成した `MarkdownViewer.exe` を右クリックメニューから起動できるように登録するスクリプトが用意されています。
```powershell
# exe ファイルを指定して登録
python register_context_menu.py path\to\MarkdownViewer.exe
```
実行後、`.md` ファイルを右クリックすると **Markdown Viewer** が表示されます。

## コンテキストメニュー解除
```powershell
python register_context_menu.py --uninstall
```
