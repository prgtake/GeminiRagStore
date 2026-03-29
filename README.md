Gemini RAG Store Manager

🇺🇸 English | 🇯🇵 日本語

<a id="japanese"></a>

🇯🇵 日本語 (Japanese)

概要

Gemini RAG Store Manager は、Googleの新しい Gemini API (google-genai) を利用して、File Search Store（RAG: 検索拡張生成用のデータストア）を直感的に管理・操作できるGUIアプリケーションです。

PDFファイルのアップロードやインデックス作成から、Geminiモデル（gemini-2.0-flash）を用いたドキュメント検索・質問応答まで、すべてを一つのアプリケーションで完結させることができます。

主な機能

ストア管理: 新規 File Search Store の作成と一覧表示。

PDFアップロード: 新規ストア作成時のPDFアップロード、および既存ストアへのPDF追加機能。

RAG（質問応答）: 選択したストア内のドキュメントに対して自然言語で質問し、回答と引用元の情報を表示します。

ストアの削除・復元:

論理削除 (非表示): API上のデータは残したまま、リストから非表示にします。

表示復元: 論理削除したストアをリストに再表示します。

完全削除: API上からストアと紐づくファイルを完全に削除します。

セキュアなAPIキー管理: .env ファイル、app_config.json、または初回起動時のダイアログ入力の3つの方法でAPIキーを安全に管理します。

EXE化対応: PyInstallerなどで実行可能ファイル（.exe）に変換した際にも、設定ファイルやメタデータファイルが正しく読み込まれるようにパス解決が組み込まれています。

前提条件

Python 3.8 以上

必要なPythonパッケージ:

google-genai

python-dotenv

インストールと実行方法

リポジトリをクローンまたはダウンロードします。

必要なパッケージをインストールします。

pip install google-genai python-dotenv


アプリケーションを実行します。

python gemini_rag_store.py


環境変数の設定 (APIキー)

アプリを利用するには Google Gemini の APIキー が必要です。以下のいずれかの方法で設定してください。

.env ファイルを使用 (推奨)
プロジェクトのルートディレクトリに .env という名前のファイルを作成し、以下を記述します。

GEMINI_API_KEY=あなたのAPIキー


app_config.json を使用
同じディレクトリに app_config.json を作成し、以下のように記述します。

{
  "GEMINI_API_KEY": "あなたのAPIキー"
}


GUIダイアログから入力
上記の設定が見つからない場合、アプリの初回起動時にAPIキーを入力するダイアログが表示されます。入力されたキーは自動的に app_config.json に保存されます。

ライセンス

このプロジェクトは MIT ライセンス の元で公開されています。
Copyright (c) 2026 [Datan]

<a id="english"></a>

🇺🇸 English

Overview

Gemini RAG Store Manager is a GUI application that allows you to intuitively manage and interact with File Search Stores (data stores for Retrieval-Augmented Generation) using Google's new Gemini API (google-genai).

You can seamlessly upload PDF files, create document indexes, and ask questions using the Gemini model (gemini-2.0-flash) based on your documents, all within a single application.

Key Features

Store Management: Create new File Search Stores and view existing ones.

PDF Upload: Upload PDF files when creating a new store, and add more PDFs to existing stores.

RAG (Question Answering): Ask natural language questions to the documents in a selected store. The app provides answers along with source citations.

Store Deletion & Restoration:

Logical Deletion (Hide): Hides the store from the UI while keeping the data intact on the API.

Restore: Unhides a logically deleted store.

Hard Delete: Permanently deletes the store and its associated files from the API.

Secure API Key Management: Manages API keys securely using a .env file, app_config.json, or a prompt dialog on the first launch.

Executable (.exe) Ready: Built-in path resolution ensures that configuration and metadata files are loaded correctly even when compiled into a standalone executable using tools like PyInstaller.

Prerequisites

Python 3.8 or higher

Required Python packages:

google-genai

python-dotenv

Installation & Usage

Clone or download this repository.

Install the required dependencies:

pip install google-genai python-dotenv


Run the application:

python gemini_rag_store.py


Configuration (API Key)

You need a Google Gemini API Key to use this app. You can set it up using one of the following methods:

Using a .env file (Recommended)
Create a .env file in the root directory and add:

GEMINI_API_KEY=your_api_key_here


Using app_config.json
Create an app_config.json file in the same directory and add:

{
  "GEMINI_API_KEY": "your_api_key_here"
}


GUI Dialog Input
If no key is found at startup, a dialog will prompt you to enter your API key. It will then be automatically saved to app_config.json for future use.

License

This project is licensed under the MIT License.
Copyright (c) 2026 [Datan]