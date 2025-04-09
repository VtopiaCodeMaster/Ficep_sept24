#!/bin/bash
# Log startup
echo "Displaying image..." | tee -a /tmp/script.log
unclutter -idle 0.1 -jitter 3 -root -noevents &
# Path to your image
IMAGE_PATH="/home/item/Ficep_sept24/Data/Ficep_Logo.png"

# Display the image using feh in fullscreen mode with no decorations
feh -FZ --no-menu "$IMAGE_PATH" &
FEH_PID=$!

# Wait a moment to ensure feh window is created
sleep .5

# Log that the image is displayed
echo "Image displayed, waiting for progress bar start..." | tee -a /tmp/script.log

# Delay before starting the progress bar (adjust if necessary)
sleep 5

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
sleep 20  # Adjust this value based on your needs

openbox --replace --sm-disable &
# Hide mouse pointer

echo "Starting 00_main.py in the background..." | tee -a /tmp/script.log

/home/item/Ficep_sept24/00_main &
MAIN_PID=$!
# Wait for a short moment to ensure the main window is created
sleep 2

# Bring the main window to the front in fullscreen mode(it disable all functionality as Alt+Tab, Win ecc..)
wmctrl -r "00_main.py" -b add,fullscreen,above  # Force 00_main.py to be fullscreen and above

# Wait for 00_main.py to finish
wait $MAIN_PID
