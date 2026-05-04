@echo off
REM Build standalone Windows exe for Live Caption Copy (Windows 11, no Python needed).
REM Requires: pip install pyinstaller, then run this from project root.

set ROOT=%~dp0
cd /d "%ROOT%"

echo Building LiveCaptionCopy (main tray app)...
pyinstaller -y LiveCaptionCopy.spec
if errorlevel 1 exit /b 1

echo Building pick_region.exe...
pyinstaller -y pick_region.spec
if errorlevel 1 exit /b 1

echo Building config_gui.exe...
pyinstaller -y config_gui.spec
if errorlevel 1 exit /b 1

set MAIN=dist\LiveCaptionCopy
echo Copying pick_region.exe and config_gui.exe into %MAIN%...
copy /y dist\pick_region.exe "%MAIN%\"
copy /y dist\config_gui.exe "%MAIN%\"

echo.
echo Done. Run: %MAIN%\LiveCaptionCopy.exe
echo (You can zip or copy the folder "%MAIN%" to another PC; no Python required.)
pause
