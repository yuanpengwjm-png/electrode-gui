@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  py -3 -m venv .venv
  if errorlevel 1 (
    echo Install Python 3.10 or newer with tkinter and the Windows Python launcher, then retry.
    pause
    exit /b 1
  )
)
".venv\Scripts\python.exe" -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)"
if errorlevel 1 (
  echo This environment needs Python 3.10 or newer. Recreate .venv with a supported Python.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -m pip install -r requirements_live.txt
if errorlevel 1 (
  echo Installation failed. Check the error above and your network connection.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -c "import tkinter,numpy,scipy,matplotlib,pylsl; print('Electrode QA dependencies OK')"
if errorlevel 1 (
  pause
  exit /b 1
)
echo In VS Code select .venv\Scripts\python.exe, then press F5.
pause
