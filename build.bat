@echo off
setlocal
cd /d %~dp0

echo ============================================
echo   GeminiRagStore EXE Build Script
echo ============================================

echo [1/3] Installing/Updating dependencies...
pip install pyinstaller google-genai python-dotenv --upgrade

echo.
echo [2/3] Building EXE (This may take a minute)...
:: --noconfirm: 上書き確認をスキップ
:: --onefile: 1つのEXEにまとめる
:: --windowed: コンソールを非表示にする
:: --clean: キャッシュをクリアしてビルド
:: --name: 作成されるファイル名
python -m PyInstaller --noconfirm --onefile --windowed ^
    --name "GeminiRagStore" ^
    --clean ^
    gemini_ragstore.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================
    echo   SUCCESS: EXE is created in "dist" folder.
    echo ============================================
    
    :: 不要な .spec ファイルを削除
    if exist "GeminiRagStore.spec" del "GeminiRagStore.spec"
) else (
    echo.
    echo !!!!!!!!! ERROR: Build failed !!!!!!!!!
)

pause
