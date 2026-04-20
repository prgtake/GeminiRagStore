Gemini File Search Store 管理パネル (AiTu 2.0)

🇺🇸 English | 🇯🇵 日本語

<a id="japanese"></a>

🇯🇵 日本語 (Japanese)

概要

Gemini File Search Store 管理パネルは、Googleの新しい Gemini API (google-genai) を利用して、File Search Store（RAG: 検索拡張生成用のデータストア）を直感的に管理・操作できるGUIアプリケーションです。

PDFファイルのアップロードやインデックス作成から、Geminiモデル（デフォルト: gemini-3.1-flash-lite-preview）を用いたドキュメント検索・質問応答まで、すべてを一つのアプリケーションで完結させることができます。

主な機能

- **ストア管理**: 新規 File Search Store の作成と一覧表示。
- **PDFアップロード**: 新規ストア作成時のPDFアップロード、および既存ストアへのPDF追加機能。
- **ファイル管理**: ストア内のファイル一覧表示、および特定のファイルの削除（インデックスごと強制削除）機能。
- **RAG（質問応答）**: 選択したストア内のドキュメントに対して自然言語で質問し、回答を表示します。
- **モデルの動的変更**: 管理パネルから使用する Gemini モデル名を直接入力して即座に変更・保存できます。
- **ストアの完全削除**: API上からストアと紐づくファイルを完全に削除（Hard Delete）します。
- **セキュア・自動設定管理**:
  - APIキーは `.env` で管理します。
  - 使用モデル等の設定は実行ファイルと同階層に `app_config.json` として自動生成・保存されます。

前提条件

- Python 3.8 以上
- Google Gemini API キー

必要なPythonパッケージ:

- `google-genai`
- `python-dotenv`

インストールと実行方法

1. リポジトリをクローンまたはダウンロードします。
2. 必要なパッケージをインストールします。
   ```bash
   pip install google-genai python-dotenv
   ```
3. プロジェクトのルートディレクトリに `.env` という名前のファイルを作成し、APIキーを記述します。
   ```env
   GEMINI_API_KEY=あなたのAPIキー
   ```
4. アプリケーションを実行します。
   ```bash
   python gemini_ragstore.py
   ```

ライセンス

このプロジェクトは MIT ライセンス の元で公開されています。
Copyright (c) 2026 Datan (データン)

---

<a id="english"></a>

🇺🇸 English

Overview

Gemini File Search Store Manager (AiTu 2.0) is a GUI application that allows you to intuitively manage and interact with File Search Stores (data stores for Retrieval-Augmented Generation) using Google's new Gemini API (google-genai).

Key Features

- **Store Management**: Create new File Search Stores and view existing ones.
- **PDF Upload**: Upload PDF files when creating a new store, and add more PDFs to existing stores.
- **File Management**: View and delete specific files (including chunks/indexes) within a store.
- **RAG (Question Answering)**: Ask natural language questions to the documents in a selected store.
- **Dynamic Model Selection**: Enter and save Gemini model names directly from the management panel.
- **Hard Delete**: Permanently deletes the store and its associated files from the API.
- **Automated Configuration**:
  - Manages API keys via `.env`.
  - Application settings are automatically created and saved as `app_config.json` in the same directory as the script.

Installation & Usage

1. Clone or download this repository.
2. Install dependencies:
   ```bash
   pip install google-genai python-dotenv
   ```
3. Create a `.env` file in the root directory:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```
4. Run the application:
   ```bash
   python gemini_ragstore.py
   ```

License

This project is licensed under the MIT License.
Copyright (c) 2026 Datan (データン)
