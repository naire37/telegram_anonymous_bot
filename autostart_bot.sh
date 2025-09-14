#!/bin/bash

# Name of your script
SCRIPT_NAME="bot.py"
# Full path to the script
SCRIPT_PATH="src/bot.py"
# Path to Python executable (you can get it with `which python3`)
PYTHON_EXEC="/usr/bin/python3"
# Dina - uncomment this for your development PYTHON_EXEC="./.venv/bin/python"

# Check if the script is running
if ! pgrep -f "$SCRIPT_PATH" > /dev/null
then
    echo "$(date): $SCRIPT_NAME not running. Restarting..."
    echo "Executing $PYTHON_EXEC $SCRIPT_PATH ..."
    mkdir -p logs
    mkdir -p logs/autostart
    rm logs/autostart/prod.log
    rm logs/autostart/offtop.log
    nohup $PYTHON_EXEC "$SCRIPT_PATH" --env PROD > logs/autostart/prod.log 2>&1 &
    nohup $PYTHON_EXEC "$SCRIPT_PATH" --env OFFTOP > logs/autostart/offtop.log 2>&1 &
else
    echo "$(date): $SCRIPT_NAME is running."
fi