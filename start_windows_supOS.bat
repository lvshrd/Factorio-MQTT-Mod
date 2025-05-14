@echo off

REM Check if the environment exists
conda env list | findstr /C:"factorio_mqtt" >nul
if errorlevel 1 (
    echo Create new conda environment factorio_mqtt...
    call conda create -y -n factorio_mqtt python=3.11
) else (
    echo Environment factorio_mqtt already exists
)

REM Activate the environment
call conda activate factorio_mqtt

REM Install dependencies
pip install -r requirements.txt

REM Get the current directory
set FACTORIO_MOD_DIR=%appdata%\Factorio\mods\sup-MQTT\scripts

REM Start two python scripts
start cmd /k "cd /d %FACTORIO_MOD_DIR% && conda activate factorio_mqtt && python subscriber.py"
start cmd /k "cd /d %FACTORIO_MOD_DIR% && conda activate factorio_mqtt && python publisher.py" 