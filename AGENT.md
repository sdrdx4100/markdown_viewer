# AGENTS.md

このファイルは OpenAI Codex（および同様の AI エージェント）に対して、
本プロジェクトの開発ルールや慣習を伝えるためのガイドラインです。

---

## Project Structure
- プロジェクトルートにある `README.md` をまず参照してください。
- GUI アプリケーションの主要ソースは `src/` 以下に配置。
- テストコードは導入する場合、`tests/` ディレクトリに配置してください。

---

## Code Style
- Python コードは **PEP 8** に完全準拠してください。
- インデントはスペース4つ。
- 行末の不要な空白は禁止。
- docstring は **NumPy スタイル** を利用してください。例：

  ```python
  def func(x, y):
      """
      サンプル関数。

      Parameters
      ----------
      x : int
          説明…
      y : int
          説明…

      Returns
      -------
      int
          処理結果
      """
      return x + y
