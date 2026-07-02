@echo off
if not exist "venv\Scripts\pyinstaller.exe" (
    echo PyInstaller not found. Please ensure it is installed in venv.
    exit /b
)
echo Building Discord Orbs Earner...
venv\Scripts\pyinstaller.exe --noconsole --onefile --icon=icon.ico --name="DiscordOrbsEarner" --add-data="icon.png;." --add-data="icon.ico;." src\app.py

if not exist release mkdir release
move dist\DiscordOrbsEarner.exe release\DiscordOrbsEarner.exe
rmdir /s /q build dist
del DiscordOrbsEarner.spec
echo Build complete. Executable is in the release folder.
pause
