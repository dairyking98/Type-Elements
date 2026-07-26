@echo off
rem Launches tune.py. Does NOT auto-launch f3d - use the tuner's own
rem "Launch f3d" button (or run f3d --watch yourself) once you've
rem rendered at least once and want to see it.
rem
rem Usage:
rem   win_start.bat                              machine picker (choose Blickensderfer/Postal/...)
rem   win_start.bat config\blickensderfer.yaml   skip the picker, load directly
setlocal

cd /d "%~dp0"

if not exist .venv (
    echo .venv not found - run win_setup.bat first 1>&2
    exit /b 1
)
call .venv\Scripts\activate.bat

if "%~1"=="" (
    python tune.py
) else (
    if not exist "%~1" (
        echo config file not found: %~1 1>&2
        exit /b 1
    )
    python tune.py "%~1"
)
