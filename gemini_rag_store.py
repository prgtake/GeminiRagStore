# SPDX-License-Identifier: MIT
# Copyright (c) 2026 [Datan]
# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import filedialog, scrolledtext, simpledialog, messagebox, ttk
import tkinter.simpledialog as sd
from google import genai
from google.genai import types
import json
import os
import time
import sys
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# =====================================================
#  アプリのバージョン定義 
# =====================================================
APP_VERSION = "1.0.0"

# --- ユーティリティ関数とクラス ---

class StoreMetaManager:
    """ストアの論理削除状態などを管理するクラス"""
    def __init__(self, path="rag_store_meta.json"):
        # EXE化を考慮したパス解決
        base_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
        self.path = os.path.join(base_dir, path)
        self.data = {"stores": {}}
        self.load()

    def load(self):
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                self.data = json.load(f)

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def mark_deleted(self, store_id, display_name):
        self.data["stores"][store_id] = {
            "display_name": display_name,
            "deleted": True
        }
        self.save()

    def is_deleted(self, store_id):
        return self.data["stores"].get(store_id, {}).get("deleted", False)
    
    def restore_store(self, store_id):
        if store_id in self.data["stores"]:
            self.data["stores"][store_id]["deleted"] = False
            self.save()
            
    def remove_store(self, store_id):
        if store_id in self.data["stores"]:
            del self.data["stores"][store_id]
            self.save()

class GeminiClientManager:
    """Gemini Client の管理と共通操作"""
    def __init__(self, api_key):
        try:
            self.client = genai.Client(api_key=api_key)
        except Exception as e:
            messagebox.showerror("APIエラー", f"Gemini クライアントの初期化エラー: {e}")
            self.client = None

    def list_stores(self):
        if not self.client: return []
        try:
            return list(self.client.file_search_stores.list())
        except Exception as e:
            messagebox.showerror("APIエラー", f"ストア一覧の取得に失敗しました: {e}")
            return []

    def delete_store_and_files(self, store_name):
        if not self.client:
            raise Exception("Gemini client が初期化されていません。")
        self.client.file_search_stores.delete(
            name=store_name, 
            config={"force": True}
        )

    def query_store(self, store_name, query):
        if not self.client: return "エラー: クライアントが初期化されていません。"
        try:
            tool_config = types.GenerateContentConfig(
                tools=[
                    types.Tool(
                        file_search=types.FileSearch(
                            file_search_store_names=[store_name]
                        )
                    )
                ]
            )
            # モデル名はユーザー指定の gemini-2.5-flash 等に合わせて設定
            response = self.client.models.generate_content(
                model="gemini-2.0-flash", 
                contents=query,
                config=tool_config,
            )
            
            result = response.text + "\n\n--- 引用元 ---\n"
            sources = set()
            if response.candidates and response.candidates[0].grounding_metadata:
                for chunk in response.candidates[0].grounding_metadata.grounding_chunks:
                    if chunk.retrieved_context and chunk.retrieved_context.title:
                        sources.add(chunk.retrieved_context.title)
            
            if sources:
                for i, source in enumerate(sources, 1):
                    result += f"[{i}] {source}\n"
            else:
                result += "引用情報が見つかりませんでした。\n"
                
            return result
        except Exception as e:
            return f"エラー: 質問応答中に問題が発生しました: {e}"

# --- メインアプリケーションクラス ---

class MainApp(tk.Tk):
    def __init__(self, api_key):
        super().__init__()
        self.title(f"Gemini RAG Store 管理パネル (v{APP_VERSION})")
        self.geometry("1000x600")

        self.client_manager = GeminiClientManager(api_key)
        if not self.client_manager.client:
            self.destroy()
            return
            
        self.store_list_data = [] 
        self.store_meta = StoreMetaManager() 

        self.show_deleted_var = tk.BooleanVar(value=False) 
        
        self.log_area = scrolledtext.ScrolledText(self, wrap=tk.WORD, height=10, state=tk.DISABLED)
        self.log_area.pack(side="bottom", fill="x", padx=10, pady=(0, 10))
        self.log_message(f"AiTu RAG Store 管理パネル (v{APP_VERSION}) が起動しました。")
        
        self.create_widgets()
        self.refresh_store_list()
        
    def log_message(self, message):
        self.log_area.config(state=tk.NORMAL)
        self.log_area.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.log_area.see(tk.END)
        self.log_area.config(state=tk.DISABLED)
        self.update()

    def create_widgets(self):
        control_frame = tk.Frame(self)
        control_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Button(control_frame, text="新規ストア追加", command=lambda: NewStoreDialog(self)).pack(side='left', padx=5)
        tk.Button(control_frame, text="情報追加", command=self.open_add_file_dialog).pack(side='left', padx=5)
        
        tk.Button(control_frame, text="選択ストア非表示", fg="orange", command=self.delete_selected_store).pack(side='left', padx=5)        
        tk.Checkbutton(control_frame, text="非表示ストアを表示", variable=self.show_deleted_var, command=self.refresh_store_list).pack(side='left', padx=10)
        tk.Button(control_frame, text="選択ストア表示復元", fg="blue", command=self.restore_selected_store).pack(side='left', padx=5)
        tk.Button(control_frame, text="選択ストア完全削除", fg="red", command=self.hard_delete_selected_store).pack(side='left', padx=5)

        tk.Label(self, text="既存の File Search Store 一覧 (Store Name / Display Name)", font=('Arial', 12, 'bold')).pack(anchor='w', padx=10, pady=(10, 0))
        
        list_frame = tk.Frame(self)
        list_frame.pack(fill='x', padx=10)
        
        self.store_listbox = ttk.Treeview(list_frame, columns=('Display', 'Created'), show='headings', height=10)
        self.store_listbox.heading('Display', text='表示名')
        self.store_listbox.heading('Created', text='作成日時')
        self.store_listbox.column('Display', width=200, anchor='w')
        self.store_listbox.column('Created', width=150, anchor='w')
        self.store_listbox.pack(side="left", fill="both", expand=True)
        
        list_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.store_listbox.yview)
        list_scrollbar.pack(side="right", fill="y")
        self.store_listbox.configure(yscrollcommand=list_scrollbar.set)
        
        self.store_listbox.bind('<<TreeviewSelect>>', self.on_store_select)
        
        query_frame = tk.Frame(self, padx=10, pady=10)
        query_frame.pack(fill='x')

        tk.Label(query_frame, text="選択されたストアへの質問:", font=('Arial', 12, 'bold')).pack(anchor='w', pady=(0, 5))
        
        self.query_entry = tk.Entry(query_frame, width=80)
        self.query_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        self.query_entry.bind('<Return>', lambda event: self.query_selected_store())

        self.query_button = tk.Button(query_frame, text="質問する (6)", command=self.query_selected_store, state=tk.DISABLED)
        self.query_button.pack(side='left')
        
    def refresh_store_list(self):
        self.store_listbox.delete(*self.store_listbox.get_children())
        self.store_list_data = self.client_manager.list_stores()
        
        if self.store_list_data:
            for store in self.store_list_data:
                store_id = store.name
                if self.store_meta.is_deleted(store_id) and not self.show_deleted_var.get():
                    continue

                display_name = store.display_name if store.display_name else os.path.basename(store_id)
                create_time = store.create_time.strftime("%Y-%m-%d %H:%M:%S") if store.create_time else "N/A"
                self.store_listbox.insert('', tk.END, text=store_id, values=(display_name, create_time))
            self.log_message("ストア一覧を更新しました。")
            self.query_button.config(state=tk.DISABLED)
        else:
            self.log_message("File Search Store は見つかりませんでした。")
            
    def get_selected_store(self):
        selected_items = self.store_listbox.selection()
        if selected_items:
            store_id = self.store_listbox.item(selected_items[0], 'text')
            display_name = self.store_listbox.item(selected_items[0], 'values')[0]
            return store_id, display_name
        return None, None
        
    def on_store_select(self, event):
        store_id, display_name = self.get_selected_store()
        if store_id:
            self.log_message(f"ストア '{display_name}' ({store_id}) が選択されました。")
            self.query_button.config(state=tk.NORMAL)
        else:
            self.query_button.config(state=tk.DISABLED)

    def query_selected_store(self):
        store_id, display_name = self.get_selected_store()
        query = self.query_entry.get().strip()
        
        if not store_id: return
        if not query: return

        self.log_message(f"\n--- ストア '{display_name}' へ質問: {query} ---")
        self.log_message("Gemini が検索・回答を生成中です...")
        
        result = self.client_manager.query_store(store_id, query)
        
        self.log_message("\n--- 回答 ---")
        self.log_message(result)
        self.log_message("------------------\n")
        
    def open_add_file_dialog(self):
        store_id, display_name = self.get_selected_store()
        if not store_id:
            messagebox.showwarning("警告", "情報を追加するストアを一覧から選択してください。")
            return
        AddFileDialog(self, store_id, display_name)

    def delete_selected_store(self):
        store_id, display_name = self.get_selected_store()
        if not store_id: return
        confirm = messagebox.askyesno("確認", f"ストア「{display_name}」を非表示にします。\n（APIキー削除までデータは残ります。）\n\n続行しますか？")
        if confirm:
            self.store_meta.mark_deleted(store_id, display_name)
            self.log_message(f"🗂 ストア '{display_name}' を非表示(論理削除)にしました")
            self.refresh_store_list()

    def hard_delete_selected_store(self):
        store_id, display_name = self.get_selected_store()
        if not store_id: return
        confirm = messagebox.askyesno("最終確認", f"⚠️ 警告 ⚠️\n\nストア「{display_name}」をAPI上から完全に削除します。\n元に戻せませんが、本当によろしいですか？")
        if confirm:
            try:
                self.log_message(f"🗑 ストア '{display_name}' をAPIから完全削除中です...")
                self.client_manager.delete_store_and_files(store_id)
                self.store_meta.remove_store(store_id) 
                self.log_message(f"✅ ストア '{display_name}' を完全に削除しました。")
                self.refresh_store_list()
            except Exception as e:
                messagebox.showerror("エラー", str(e))

    def restore_selected_store(self):
        store_id, display_name = self.get_selected_store()
        if not store_id: return
        if self.store_meta.is_deleted(store_id):
            self.store_meta.restore_store(store_id)
            self.log_message(f"♻ ストア '{display_name}' を復元しました。")
            self.refresh_store_list()

# --- 新規ストア作成ダイアログ ---

class NewStoreDialog(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.title("新規 File Search Store の追加")
        self.geometry("600x500")
        self.transient(master)
        self.grab_set()
        self.client = master.client_manager.client
        self.file_path = None
        self.file_search_store_name = None 
        self.create_widgets()
        
    def create_widgets(self):
        upload_frame = tk.LabelFrame(self, text="① PDFファイルのアップロード (ファイル名がストア名になります)", padx=10, pady=10)
        upload_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Button(upload_frame, text="ファイルを選択", command=self.select_file).pack(side='left')
        self.file_label = tk.Label(upload_frame, text="ファイルが選択されていません", fg="red")
        self.file_label.pack(side='left', padx=10)
        
        tk.Button(upload_frame, text="アップロード", command=self.upload_and_index).pack(side='right')

        query_frame = tk.LabelFrame(self, text="② 質問", padx=10, pady=10)
        query_frame.pack(fill='x', padx=10, pady=5)
        
        self.query_entry = tk.Entry(query_frame, width=60)
        self.query_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        self.query_button = tk.Button(query_frame, text="質問する", command=self.ask_question, state=tk.DISABLED)
        self.query_button.pack(side='left')

        tk.Label(self, text="結果/ログ:", font=('Arial', 10, 'bold')).pack(anchor='w', padx=10, pady=(0, 5))
        self.log_area = scrolledtext.ScrolledText(self, wrap=tk.WORD, height=10, state=tk.DISABLED)
        self.log_area.pack(fill='both', expand=True, padx=10, pady=(0, 10))

    def log_message(self, message):
        self.log_area.config(state=tk.NORMAL)
        self.log_area.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.log_area.see(tk.END)
        self.log_area.config(state=tk.DISABLED)
        self.update()
        
    def select_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if self.file_path:
            self.file_label.config(text=os.path.basename(self.file_path), fg="blue")

    def upload_and_index(self):
        if not self.file_path: return
        base_name = os.path.basename(self.file_path)
        display_name = os.path.splitext(base_name)[0]
        
        self.log_message(f"--- File Search Store の作成を開始 (ストア名: {display_name}) ---")
        try:
            store = self.client.file_search_stores.create(config={"display_name": display_name})
            self.file_search_store_name = store.name
            self.log_message(f"ストアが作成されました。名前: {store.name}")
            
            operation = self.client.file_search_stores.upload_to_file_search_store(
                file=self.file_path,
                file_search_store_name=self.file_search_store_name,
                config={"display_name": base_name}
            )

            while not operation.done:
                self.log_message("インデックス作成中... (3秒待機)")
                time.sleep(3)
                operation = self.client.operations.get(operation)

            self.log_message("--- インデックス作成が完了しました！ ---")
            self.query_button.config(state=tk.NORMAL)
            self.master.refresh_store_list()
        except Exception as e:
            self.log_message(f"❌ エラー: {e}")

    def ask_question(self):
        query = self.query_entry.get().strip()
        if not query or not self.file_search_store_name: return
        self.log_message(f"\n--- 質問: {query} ---")
        result = self.master.client_manager.query_store(self.file_search_store_name, query)
        self.log_message(f"\n--- 回答 ---\n{result}\n")

class AddFileDialog(NewStoreDialog):
    def __init__(self, master, store_id, display_name):
        tk.Toplevel.__init__(self, master)
        self.master = master
        self.title(f"既存ストアへの情報追加: {display_name}")
        self.geometry("600x500")
        self.transient(master)
        self.grab_set()

        self.client = master.client_manager.client
        self.file_path = None
        self.file_search_store_name = store_id 
        self.display_name = display_name
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text=f"選択中のストア: {self.display_name}").pack(anchor='w', padx=10, pady=5)
        
        upload_frame = tk.LabelFrame(self, text="② PDFファイルの追加アップロード", padx=10, pady=10)
        upload_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Button(upload_frame, text="ファイルを選択", command=self.select_file).pack(side='left')
        self.file_label = tk.Label(upload_frame, text="ファイルが選択されていません", fg="red")
        self.file_label.pack(side='left', padx=10)
        tk.Button(upload_frame, text="アップロード", command=self.upload_and_index).pack(side='right')

        query_frame = tk.LabelFrame(self, text="③ 質問", padx=10, pady=10)
        query_frame.pack(fill='x', padx=10, pady=5)
        self.query_entry = tk.Entry(query_frame, width=60)
        self.query_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        self.query_button = tk.Button(query_frame, text="質問する", command=self.ask_question, state=tk.NORMAL)
        self.query_button.pack(side='left')

        self.log_area = scrolledtext.ScrolledText(self, wrap=tk.WORD, height=10, state=tk.DISABLED)
        self.log_area.pack(fill='both', expand=True, padx=10, pady=(0, 10))

# --- メイン処理 ---

if __name__ == "__main__":
    # 実行環境に基づいたベースディレクトリの取得
    base_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
    CONFIG_FILE = os.path.join(base_dir, "app_config.json")
    
    api_key = os.environ.get("GEMINI_API_KEY")

    # app_config.json からの読み込み
    if not api_key and os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                api_key = json.load(f).get("GEMINI_API_KEY")
        except Exception:
            pass

    # キーがない場合はダイアログで入力を求める
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        root = tk.Tk()
        root.withdraw()
        key = sd.askstring("API キー", "Gemini API キーを入力してください：\n（app_config.json に保存されます）", parent=root)
        root.destroy()

        if not key:
            sys.exit()
            
        api_key = key
        # app_config.json への保存
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump({"GEMINI_API_KEY": api_key}, f)
        except Exception as e:
            print(f"設定保存失敗: {e}")

    # アプリ起動
    app = MainApp(api_key)
    app.mainloop()