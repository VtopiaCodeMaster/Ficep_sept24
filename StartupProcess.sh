#!/bin/bash

# Run unclutter to hide the mouse cursor after 1 second of inactivity
unclutter -idle 1 -jitter 3 -root -noevents &

# Store the unclutter process ID to manage later if needed
UNCLUTTER_PID=$!

# Log unclutter start
echo "Unclutter started with PID: $UNCLUTTER_PID"

# Start 00_main.py in the background
echo "Starting 00_main.py in the background..."
python3 /home/item/Ficep_sept24/00_main.py &
MAIN_PID=$!

# Log main process start
echo "00_main.py started with PID: $MAIN_PID"

# Run the StartupProgressBar Python script in the foreground
echo "Starting progress bar script..."
python3 /home/item/Ficep_sept24/StartupProgressBar.py

# Kill unclutter process after progress bar script finishes
echo "Killing unclutter process..."
kill $UNCLUTTER_PID

# Bring the 00_main.py window to the foreground after progress bar finishes
echo "Bringing 00_main.py to the foreground..."
wmctrl -R "00_main.py"

# Keep the script running without closing the main process
echo "Main process continues running in the background."

# Wait for the main process to finish (will not terminate unless main is manually closed)
wait $MAIN_PID
