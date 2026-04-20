# MIT License
# 
# Copyright (c) 2026 Datan (データン)
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, ttk, simpledialog
from google import genai
from google.genai import types
import os
import time
import json
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# 実行ファイルのディレクトリを取得して絶対パスを作成
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "app_config.json")

class GeminiClientManager:
    def __init__(self):
        self.config = self._load_config()
        # 保存されたモデル名があれば使用、なければデフォルト
        self.current_model = self.config.get("model", "gemini-3.1-flash-lite-preview")
        
        # 初回起動時（ファイルがない場合）にデフォルト設定でファイルを作成しておく
        if not os.path.exists(CONFIG_FILE):
            self._save_config()

        try:
            self.client = genai.Client()
        except Exception as e:
            messagebox.showerror("APIエラー", f"Gemini 初期化エラー: {e}")
            self.client = None

    def _load_config(self):
        """設定ファイルから情報を読み込む"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_config(self):
        """現在の設定をファイルに保存する"""
        self.config["model"] = self.current_model
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"設定の保存に失敗しました: {e}")

    def set_model(self, model_name):
        """使用モデルを変更し保存する"""
        self.current_model = model_name
        self._save_config()

    def list_stores(self):
        """ストア一覧を取得"""
        if not self.client: return []
        try:
            return list(self.client.file_search_stores.list())
        except Exception as e:
            return []

    def list_files_in_store(self, store_name):
        """'documents' 階層を使用してファイルをリストアップ"""
        if not self.client: return "Error", []
        try:
            res_iter = self.client.file_search_stores.documents.list(parent=store_name)
            res = list(res_iter)
            return "DEBUG: documents.list を実行しました", self._format_results(res)
        except Exception as e:
            return f"DEBUG: 実行エラー: {e}", e

    def _format_results(self, res_list):
        enriched = []
        for f in res_list:
            dname = getattr(f, 'display_name', getattr(f, 'title', "（名称未設定）"))
            rname = getattr(f, 'name', "Unknown ID")
            enriched.append({"display_name": dname, "resource_name": rname})
        return enriched

    def delete_file_from_store(self, store_name, file_name):
        """特定のファイルを削除（forceオプションを追加）"""
        try:
            # config={"force": True} を追加することで、
            # 内部で生成されたインデックス（チャンク）ごと強制的に削除します
            self.client.file_search_stores.documents.delete(
                name=file_name, 
                config={"force": True}
            )
            return True
        except Exception as e:
            return e

    def update_store_display_name(self, store_name, new_display_name):
        """ストアの表示名を更新（update メソッドを試行）"""
        try:
            # 'patch' ではなく 'update' が正解であるケースが多いです
            # もし update も patch も無い場合は、AttributeError が返ります
            if hasattr(self.client.file_search_stores, 'update'):
                self.client.file_search_stores.update(
                    name=store_name,
                    display_name=new_display_name
                )
                return True
            else:
                return "このSDKバージョンではストア名の変更（update/patch）がサポートされていないようです。"
        except Exception as e:
            return e

    def delete_store_and_files(self, store_name):
        """ストアをAPIから完全削除"""
        try:
            self.client.file_search_stores.delete(name=store_name, config={"force": True})
            return True
        except Exception as e:
            return e

    def query_store(self, store_name, query):
        if not self.client: return "エラー: 未初期化"
        try:
            tool_config = types.GenerateContentConfig(
                tools=[types.Tool(file_search=types.FileSearch(file_search_store_names=[store_name]))]
            )
            response = self.client.models.generate_content(
                model=self.current_model,
                contents=query,
                config=tool_config,
            )
            return response.text
        except Exception as e:
            return f"エラー: {e}"

# --- メインアプリケーションクラス ---

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gemini File Search Store 管理パネル")
        self.geometry("1100x750")

        self.client_manager = GeminiClientManager()
        if not self.client_manager.client:
            self.destroy()
            return
        
        self.create_widgets()
        self.refresh_store_list()
        
    def log_message(self, message):
        self.log_area.config(state=tk.NORMAL)
        self.log_area.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.log_area.see(tk.END)
        self.log_area.config(state=tk.DISABLED)
        self.update()

    def create_widgets(self):
        # 0. ステータス情報（最上部）
        info_frame = tk.Frame(self, bg="#f0f0f0", pady=5)
        info_frame.pack(fill='x')
        
        # APIキーの伏せ字処理
        api_key = os.environ.get("GEMINI_API_KEY", "N/A")
        masked_key = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) > 10 else api_key

        tk.Label(
            info_frame, 
            text=f"🔑 API Key: {masked_key}",
            font=('Arial', 9),
            bg="#f0f0f0",
            fg="#555555"
        ).pack(side='left', padx=10)

        # モデル名入力用テキストボックス
        tk.Label(
            info_frame, 
            text="🤖 Model:",
            font=('Arial', 9),
            bg="#f0f0f0",
            fg="#555555"
        ).pack(side='left', padx=(20, 5))

        self.model_var = tk.StringVar(value=self.client_manager.current_model)
        self.model_entry = tk.Entry(info_frame, textvariable=self.model_var, width=35)
        self.model_entry.pack(side='left', padx=5)
        self.model_entry.bind('<Return>', lambda e: self.update_model_from_ui())

        tk.Button(
            info_frame, 
            text="適用", 
            command=self.update_model_from_ui,
            font=('Arial', 8),
            padx=5
        ).pack(side='left', padx=2)

        # 1. 上部コントロール
        control_frame = tk.Frame(self)
        control_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Button(control_frame, text="新規ストア作成", command=lambda: NewStoreDialog(self), width=18).pack(side='left', padx=5)
        tk.Button(control_frame, text="指定ストアにPDF追加", command=self.open_add_file_dialog, width=18).pack(side='left', padx=5)
        # tk.Button(control_frame, text="ストア名変更", command=self.rename_selected_store, width=18).pack(side='left', padx=5) #ストア名変更はAPIの現バージョンはサポートしていないコメントアウト
        tk.Button(control_frame, text="指定ストア削除", fg="red", command=self.hard_delete_selected_store, width=18).pack(side='right', padx=5)

        # 2. メインコンテンツ（左右分割）
        paned = tk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill="both", expand=True, padx=10, pady=5)

        # 左側: ストア一覧
        left_frame = tk.Frame(paned)
        paned.add(left_frame, width=500)
        tk.Label(left_frame, text="① 科目（ストア）一覧", font=('Arial', 10, 'bold')).pack(anchor='w')
        self.store_listbox = ttk.Treeview(left_frame, columns=('Display', 'Created'), show='headings', height=10)
        self.store_listbox.heading('Display', text='表示名')
        self.store_listbox.heading('Created', text='作成日時')
        self.store_listbox.pack(fill="both", expand=True)
        self.store_listbox.bind('<<TreeviewSelect>>', self.on_store_select)

        # 右側: ファイル一覧
        right_frame = tk.Frame(paned)
        paned.add(right_frame, width=550)
        tk.Label(right_frame, text="② 登録済みファイル（図解・教材）", font=('Arial', 10, 'bold')).pack(anchor='w')
        
        self.file_listbox = ttk.Treeview(right_frame, columns=('FileName', 'ID'), show='headings', height=10)
        self.file_listbox.heading('FileName', text='ファイル名')
        self.file_listbox.heading('ID', text='リソースID')
        self.file_listbox.column('FileName', width=200)
        self.file_listbox.pack(fill="both", expand=True)
        
        btn_file_delete = tk.Button(right_frame, text="指定されたファイルを削除", fg="red", command=self.delete_selected_file, width=18)
        btn_file_delete.pack(pady=5, anchor='e')

        # 3. 質問セクション
        query_frame = tk.Frame(self, padx=10, pady=10)
        query_frame.pack(fill='x')
        self.query_entry = tk.Entry(query_frame)
        self.query_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        self.query_entry.bind('<Return>', lambda e: self.query_selected_store())
        self.query_button = tk.Button(query_frame, text="指定ストアに質問", command=self.query_selected_store, state=tk.DISABLED, width=18)
        self.query_button.pack(side='left')
        
        # 4. ログ
        self.log_area = scrolledtext.ScrolledText(self, wrap=tk.WORD, height=8, state=tk.DISABLED)
        self.log_area.pack(fill="x", padx=10, pady=10)

    def update_model_from_ui(self):
        """テキストボックスからモデル名を取得して更新"""
        new_model = self.model_var.get().strip()
        if new_model:
            self.client_manager.set_model(new_model)
            self.log_message(f"✅ 使用モデルを '{new_model}' に更新・保存しました。")
        else:
            messagebox.showwarning("警告", "モデル名を入力してください。")

    def refresh_store_list(self):
        self.store_listbox.delete(*self.store_listbox.get_children())
        stores = self.client_manager.list_stores()
        for s in stores:
            display = s.display_name if s.display_name else os.path.basename(s.name)
            time_str = s.create_time.strftime("%Y-%m-%d %H:%M") if s.create_time else "N/A"
            self.store_listbox.insert('', tk.END, text=s.name, values=(display, time_str))
        self.log_message("ストア一覧を更新しました。")

    def on_store_select(self, event):
        sid, dname = self.get_selected_store()
        if sid:
            self.query_button.config(state=tk.NORMAL)
            self.refresh_file_list(sid)

    def refresh_file_list(self, store_id):
        self.file_listbox.delete(*self.file_listbox.get_children())
        debug_info, res = self.client_manager.list_files_in_store(store_id)
        if isinstance(res, list):
            for f in res:
                self.file_listbox.insert('', tk.END, text=f["resource_name"], values=(f["display_name"], f["resource_name"]))
        else:
            self.log_message(f"❌ 取得失敗: {res}")

    def rename_selected_store(self):
        sid, old_name = self.get_selected_store()
        if not sid: return
        new_name = simpledialog.askstring(
            "ストア名の変更", 
            "新しい表示名を入力してください:", 
            initialvalue=old_name,
            parent=self
        )
        if new_name and new_name != old_name:
            self.log_message(f"ストア名変更をリクエスト中: {new_name}...")
            res = self.client_manager.update_store_display_name(sid, new_name)
            
            if res is True:
                self.log_message(f"✅ ストア名を '{new_name}' に変更しました。")
                self.refresh_store_list()
            else:
                # 失敗した場合に原因をポップアップで表示します
                messagebox.showerror("変更失敗", f"APIエラーが発生しました:\n{res}")
                self.log_message(f"❌ 変更失敗: {res}")

    def delete_selected_file(self):
        """選択したファイルを削除（エラー表示と待機処理を追加）"""
        sid, _ = self.get_selected_store()
        selected = self.file_listbox.selection()
        if not selected: return
        
        fid = self.file_listbox.item(selected[0], 'text')
        fname = self.file_listbox.item(selected[0], 'values')[0]
        
        if messagebox.askyesno("確認", f"ファイル '{fname}' を削除しますか？"):
            self.log_message(f"ファイル削除をリクエスト中: {fname}...")
            
            # 実行結果を受け取る
            res = self.client_manager.delete_file_from_store(sid, fid)
            
            if res is True:
                self.log_message("✅ サーバーへ削除を依頼しました。")
                self.log_message("インデックスの更新に数秒かかるため、2秒後にリストを自動更新します...")
                
                # 削除直後はリストに残ることが多いため、2秒待ってからリフレッシュ
                self.after(2000, lambda: self.refresh_file_list(sid)) 
            else:
                # True以外（エラーオブジェクトなど）が返ってきたらエラーを表示
                messagebox.showerror("削除失敗", f"エラーが発生しました:\n{res}")
                self.log_message(f"❌ 削除失敗: {res}")

    def hard_delete_selected_store(self):
        sid, dname = self.get_selected_store()
        if not sid: return
        msg = f"⚠️ 警告 ⚠️\n\nストア「{dname}」を完全に削除します。\n中身のPDFや図解データもすべて消失し、復元できません。\n\n本当に削除しますか？"
        if messagebox.askyesno("最終確認", msg):
            if self.client_manager.delete_store_and_files(sid) is True:
                self.log_message(f"🗑️ ストア '{dname}' を完全に削除しました。")
                self.refresh_store_list()

    def get_selected_store(self):
        items = self.store_listbox.selection()
        if items:
            return self.store_listbox.item(items[0], 'text'), self.store_listbox.item(items[0], 'values')[0]
        return None, None

    def query_selected_store(self):
        sid, dname = self.get_selected_store()
        query = self.query_entry.get().strip()
        if not sid or not query: return
        self.log_message(f"--- '{dname}' へ質問: {query} ---")
        self.log_message(self.client_manager.query_store(sid, query))

    def open_add_file_dialog(self):
        sid, dname = self.get_selected_store()
        if not sid: return
        AddFileDialog(self, sid, dname)

# --- ダイアログ系 ---

class NewStoreDialog(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.title("新規 RAG Store 作成")
        self.geometry("500x450")

        # ダイアログを最前面に表示し、親ウィンドウへの操作を制限する設定
        self.transient(master)   # 親ウィンドウの上に常時表示
        self.grab_set()          # モーダル（このウィンドウを閉じるまで親を操作不可）
        self.focus_set()         # フォーカスをセット
        
        self.client = master.client_manager.client
        self.file_path = None
        self.create_widgets()
        
    def log_message(self, message):
        self.log.config(state=tk.NORMAL)
        self.log.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.log.see(tk.END)
        self.log.config(state=tk.DISABLED)
        self.update()

    def create_widgets(self):
        container = tk.Frame(self, padx=20, pady=10)
        container.pack(fill="both", expand=True)

        tk.Button(container, text="PDFを選択", width=22, command=self.select_file).pack(anchor='w', pady=5)
        
        self.lbl = tk.Label(container, text="未選択", fg="red")
        self.lbl.pack(anchor='w', pady=5)
        
        tk.Button(container, text="アップロード & ストア作成", width=22, command=self.upload).pack(anchor='w', pady=5)
        
        tk.Label(container, text="取り込み経過:", font=('Arial', 9, 'bold')).pack(anchor='w', pady=(10, 0))
        self.log = scrolledtext.ScrolledText(container, height=12, state=tk.DISABLED)
        self.log.pack(fill="both", expand=True, pady=5)

    def select_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if self.file_path:
            self.lbl.config(text=os.path.basename(self.file_path), fg="blue")
            self.log_message(f"ファイルを選択しました: {os.path.basename(self.file_path)}")

    def upload(self):
        if not self.file_path:
            messagebox.showwarning("警告", "PDFファイルを選択してください。")
            return
        dname = os.path.splitext(os.path.basename(self.file_path))[0]
        try:
            self.log_message(f"RAGストア '{dname}' を作成中...")
            store = self.client.file_search_stores.create(config={"display_name": dname})
            
            self.log_message(f"ファイルをアップロード中: {os.path.basename(self.file_path)}...")
            op = self.client.file_search_stores.upload_to_file_search_store(
                file=self.file_path, file_search_store_name=store.name, config={"display_name": os.path.basename(self.file_path)}
            )
            
            self.log_message("サーバー側でインデックス作成中（数秒かかります）...")
            while not op.done:
                time.sleep(2)
                op = self.client.operations.get(op)
            
            self.log_message("✅ すべての処理が完了しました。")
            messagebox.showinfo("完了", "ストア作成完了")
            self.master.refresh_store_list()
            self.destroy()
        except Exception as e:
            self.log_message(f"❌ エラーが発生しました: {e}")
            messagebox.showerror("エラー", str(e))

class AddFileDialog(NewStoreDialog):
    def __init__(self, master, sid, dname):
        tk.Toplevel.__init__(self, master)
        self.master, self.sid, self.dname = master, sid, dname
        self.title(f"追加: {dname}")
        self.geometry("500x450")

        # ダイアログを最前面に表示し、親ウィンドウへの操作を制限する設定
        self.transient(master)
        self.grab_set()
        self.focus_set()

        self.client = master.client_manager.client
        self.file_path = None
        self.create_widgets()

    def upload(self):
        if not self.file_path:
            messagebox.showwarning("警告", "PDFファイルを選択してください。")
            return
        try:
            self.log_message(f"ストア '{self.dname}' へファイルを追加アップロード中...")
            op = self.client.file_search_stores.upload_to_file_search_store(
                file=self.file_path, file_search_store_name=self.sid, config={"display_name": os.path.basename(self.file_path)}
            )
            
            self.log_message("サーバー側でインデックス更新中...")
            while not op.done:
                time.sleep(2)
                op = self.client.operations.get(op)
            
            self.log_message("✅ 追記が完了しました。")
            messagebox.showinfo("完了", "追記完了")
            self.master.refresh_file_list(self.sid)
            self.destroy()
        except Exception as e:
            self.log_message(f"❌ エラーが発生しました: {e}")
            messagebox.showerror("エラー", str(e))

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()