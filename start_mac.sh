#!/bin/bash

if ! conda env list | grep -q "factorio_agent_env"; then
    echo "Creating new conda environment factorio_agent_env..."
    conda create -n factorio_agent_env python=3.11
    # Activate conda environment
    conda activate factorio_agent_env

    # Install dependencies
    pip install -r requirements.txt
else
    echo "Conda environment factorio_agent_env already exists"
fi

# Get current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FACTORIO_MOD_DIR="${SCRIPT_DIR}/scripts"

# Start two python scripts
osascript -e "tell application \"Terminal\" to do script \"cd '$FACTORIO_MOD_DIR' && conda activate factorio_agent_env && python subscriber.py\""
osascript -e "tell application \"Terminal\" to do script \"cd '$FACTORIO_MOD_DIR' && conda activate factorio_agent_env && python publisher.py\""

# 关闭当前终端窗口
osascript -e 'tell application "Terminal" to close every window whose name contains "start_mac.sh"'