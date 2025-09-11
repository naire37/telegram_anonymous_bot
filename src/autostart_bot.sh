#!/bin/bash

# Name of your script
SCRIPT_NAME="bot_latest_stable_version.py"
# Full path to the script
SCRIPT_PATH="ships_bot/bot_latest_stable_version.py"
# Path to Python executable (you can get it with `which python3`)
PYTHON_EXEC="/usr/bin/python3"

# Check if the script is running
if ! pgrep -f "$SCRIPT_PATH" > /dev/null
then
    echo "$(date): $SCRIPT_NAME not running. Restarting..."
    echo "Executing $PYTHON_EXEC $SCRIPT_PATH ..."
    nohup $PYTHON_EXEC "$SCRIPT_PATH" > /tmp/my_script.log 2>&1 &
else
    echo "$(date): $SCRIPT_NAME is running."
fi
