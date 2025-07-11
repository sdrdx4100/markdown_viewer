# Markdown Viewer

Windows向けMarkdownビューア・エディタ

## 概要
- 左ペインでMarkdownを編集し、右ペインでリアルタイムプレビュー
- PySide6 + QtWebEngineでGUIを実装
- `markdown`パッケージでMarkdown→HTML変換
- PyInstallerで単一のexe化
- Windowsのエクスプローラー右クリックメニューに登録可能

## ファイル構成
```
markdown_viewer/
├── main.py                # メインアプリケーション
├── register_context_menu.py  # 右クリックメニュー登録・解除スクリプト
├── requirements.txt
├── build.ps1              # ビルド用PowerShellスクリプト
├── README.md
└── .vscode/
    └── tasks.json
```

## 開発環境準備
```powershell
cd <project_root>
python -m venv .venv
.\.venv\Scripts\Activate
pip install -r requirements.txt
```

## ビルド
```powershell
# PowerShellスクリプト実行
.\build.ps1
```

## コンテキストメニュー登録
```powershell
# ビルド後、Distフォルダに生成されたMarkdownViewer.exeを
# register_context_menu.exe（または直接register_context_menu.pyを実行）へリネームしてから実行
.
# 例: 
copy .\dist\MarkdownViewer.exe .\register_context_menu.exe
.
# 登録
.
# 右クリックで「Markdown Viewer」が表示されるようになる
```

## コンテキストメニュー解除
```powershell
register_context_menu.exe --uninstall
```
