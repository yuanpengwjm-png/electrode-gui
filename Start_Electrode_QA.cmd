@echo off
setlocal
cd /d "%~dp0"
set "QA_PYTHON=%~dp0.venv\Scripts\python.exe"
if not exist "%QA_PYTHON%" set "QA_PYTHON=%~dp0..\.venv-lsl\Scripts\python.exe"
if not exist "%QA_PYTHON%" (
  echo Run Setup_Environment.cmd once before starting this checkout.
  pause
  exit /b 1
)
"%QA_PYTHON%" -c "import tkinter,numpy,scipy,matplotlib,pylsl"
if errorlevel 1 (
  echo Dependency check failed. Run Setup_Environment.cmd and read its output.
  pause
  exit /b 1
)
"%QA_PYTHON%" "%~dp0live_main.py" %*
if errorlevel 1 pause
