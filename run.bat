@echo off
REM Interview Agent — Easy launcher for Windows

set PYTHONUTF8=1

if "%1"=="--demo" (
    echo Running DEMO CLI mode (no API key needed)...
    .\venv\Scripts\python.exe agent.py --demo
) else if "%1"=="--web" (
    echo Launching WEB Application...
    .\venv\Scripts\streamlit.exe run app.py
) else if "%1"=="--live" (
    echo Running LIVE CLI interview mode...
    .\venv\Scripts\python.exe agent.py
) else (
    echo Usage:
    echo   run.bat --web     ^(launch Web Application UI in browser^)
    echo   run.bat --demo    ^(replay sample transcript in terminal^)
    echo   run.bat --live    ^(interactive interview in terminal^)
    echo.
    echo Launching WEB Application by default...
    .\venv\Scripts\streamlit.exe run app.py
)
