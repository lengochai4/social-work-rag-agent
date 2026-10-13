@echo off
setlocal

rem Detect Python binary (prefer virtual environments if present)
set "PY=python"
if exist ".venv\Scripts\python.exe" (
    set "PY=.venv\Scripts\python.exe"
) else if exist "..\.venv\Scripts\python.exe" (
    set "PY=..\.venv\Scripts\python.exe"
)

if "%1"=="" goto help
if "%1"=="help" goto help
if "%1"=="setup" goto setup
if "%1"=="demo" goto demo
if "%1"=="eval" goto eval
if "%1"=="test" goto test
goto unknown

:help
echo ==========================================================
echo AIPR FINAL PROJECT - SOCIAL WORK (CTXH) RAG AGENT
echo ==========================================================
echo Available commands:
echo   make setup - Install dependencies and prepare directories
echo   make demo  - Run 3-layer ReAct Agent live demo
echo   make eval  - Run evaluation benchmark on 12 test queries
echo   make test  - Run unit test suite (pytest tests/ -v)
goto end

:setup
%PY% -m pip install -r requirements.txt
%PY% -c "import sys; print('Python runtime verified:', sys.version)"
%PY% -c "from pathlib import Path; Path('data/db').mkdir(parents=True, exist_ok=True); Path('logs').mkdir(parents=True, exist_ok=True); Path('results').mkdir(parents=True, exist_ok=True)"
goto end

:demo
%PY% run_demo.py
goto end

:eval
%PY% run_evaluation.py
goto end

:test
%PY% -m pytest tests/ -v
goto end

:unknown
echo Unknown target: %1
echo Run "make help" for usage.
goto end

:end
endlocal
