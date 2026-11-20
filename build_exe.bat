@echo off
echo ========================================================
echo        Building EduTrack Standalone Executable (.exe)
echo ========================================================
echo.

if not exist ".venv\Scripts\pyinstaller.exe" (
    echo [INFO] Installing PyInstaller in virtual environment...
    .venv\Scripts\python.exe -m pip install pyinstaller
)

echo [INFO] Building EduTrack.exe with Per-Monitor DPI awareness manifest...
.venv\Scripts\pyinstaller.exe --noconfirm --clean --onefile --windowed --name "EduTrack" --icon "assets/edutrack-icon.ico" --manifest "EduTrack.manifest" --add-data "assets;assets" --add-data "web_ui;web_ui" --add-data "database/schema.sql;database" --collect-all customtkinter --collect-all reportlab --collect-all webview --collect-all sklearn main.py

echo.
if exist "dist\EduTrack.exe" (
    echo ========================================================
    echo [SUCCESS] Build completed successfully!
    echo Executable location: dist\EduTrack.exe
    echo ========================================================
) else (
    echo [ERROR] Build failed. Check the error log above.
)
pause
