#!/bin/bash
# Log startup
echo "Starting Mouse.sh..." | tee -a /tmp/script.log
/home/item/Vtopia_Nord_BEV/Mouse.sh

echo "Displaying image..." | tee -a /tmp/script.log

# Path to your image
IMAGE_PATH="/home/item/Ficep_sept24/Ficep_Logo.png"

# Display the image using feh in a new window
feh -FZ "$IMAGE_PATH" &
FEH_PID=$!

# Wait a moment to ensure feh window is created
sleep .5

# Log that the image is displayed
echo "Image displayed, waiting for progress bar start..." | tee -a /tmp/script.log

# Delay before starting the progress bar (adjust if necessary)
sleep 2

# Kill the feh process to close the image
echo "Closing image and starting progress bar..." | tee -a /tmp/script.log
kill $FEH_PID

# Start the progress bar in the background
python3 /home/item/Ficep_sept24/StartupProgressBar.py &
PROGRESS_BAR_PID=$!

# Log the progress bar PID
echo "Progress bar PID: $PROGRESS_BAR_PID" | tee -a /tmp/script.log

# Small delay to ensure the progress bar window is created and visible
sleep .5

# Log progress bar is running
echo "Progress bar started, waiting before starting 00_main.py..." | tee -a /tmp/script.log

# Delay the start of 00_main.py (adjust this delay as necessary)
sleep 52  # Adjust this value based on your needs

echo "Starting 00_main.py in the background..." | tee -a /tmp/script.log
python3 /home/item/Ficep_sept24/00_main.py &
MAIN_PID=$!

# Wait for 00_main.py to finish
wait $MAIN_PID
