Gemini RAG Store Management Panel

English | 日本語

<a name="english"></a>

English

Gemini RAG Store Management Panel is a desktop application designed for intuitive management and operation of the "File Search (RAG)" feature within the Google Gemini API. It allows users to create their own knowledge bases (Stores) by uploading PDF files and interact with AI based on that knowledge, even without prior programming knowledge.

🚀 Key Features

File Search Store Management: Easily create and manage new knowledge bases (Stores).

PDF Upload & Automatic Indexing: Simply upload a PDF, and Gemini automatically processes it into a searchable state.

RAG Interaction: Ask questions based specifically on the content of the selected store. Includes a feature to display citations (sources) in the answers.

Flexible Deletion Management:

Logical Deletion (Hide): Hide from the list while retaining data on the server.

Complete Deletion: Permanently erase data from the server via the API.

Cross-platform Support: Runs on Windows, Mac, and Linux environments wherever Python is available (built using Tkinter).

🛠 Prerequisites

Python 3.10 or higher

Gemini API Key: Obtain it from Google AI Studio.

Library Installation:

pip install google-genai python-dotenv


📦 Setup and Execution

Clone or download this repository.

API Key Configuration:

.env file: Create a file named .env and add GEMINI_API_KEY=your_key_here.

App Startup: A dialog will appear upon the first startup for you to enter the key (it will be saved in app_config.json).

Run the application:

python gemini_rag_store.py


<a name="japanese"></a>

日本語

Gemini RAG Store Management Panel は、Google Gemini APIの「File Search（RAG）」機能を直感的に操作・管理するためのデスクトップアプリケーションです。プログラミングの知識がなくても、PDFファイルをアップロードして独自の知識ベース（Store）を作成し、AIと対話させることができます。

🚀 主な機能

File Search Store の作成・管理: 新しいナレッジベース（ストア）を簡単に作成。

PDFアップロード & 自動インデックス: PDFをアップロードするだけで、Geminiが検索可能な状態に自動で処理。

RAG対話機能: 選択したストアの内容に基づいた質問応答。回答には引用元（ソース）の表示機能付き。

柔軟な削除管理:

非表示（論理削除）: 一覧から隠すだけでデータを保持。

完全削除: API経由でサーバー上のデータを完全に消去。

マルチプラットフォーム対応: Pythonが動作する環境であれば、Windows/Mac/Linuxで利用可能。

🛠 準備するもの

Python 3.10以上

Gemini API キー: Google AI Studio から取得してください。

ライブラリのインストール:

pip install google-genai python-dotenv


📦 セットアップと実行

リポジトリをクローンまたはダウンロードします。

APIキーの設定:

.envファイル: .env ファイルを作成し、GEMINI_API_KEY=あなたのキー と記述。

アプリ起動時: 初回起動時にダイアログが表示されるので、そこで入力（app_config.json に保存されます）。

アプリを起動します:

python gemini_rag_store.py


⚖️ License

This project is released under the MIT License.
Copyright (c) 2026 [Datan]