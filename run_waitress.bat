@echo off
REM Run serve_waitress.py using virtualenv python if present, otherwise system python
IF EXIST "%~dp0\.venv\Scripts\python.exe" (
  "%~dp0\.venv\Scripts\python.exe" "%~dp0\serve_waitress.py"
) ELSE (
  python "%~dp0\serve_waitress.py"
)
