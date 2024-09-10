import evdev
from evdev import InputDevice, categorize, ecodes
#may have effect after reboot
#sudo usermod -aG input item

#works, but (1) need to be done after every reboot, (2) does not allow autonomous touch detection
#sudo chmod a+r /dev/input/event3

# Replace '/dev/input/eventX' with the correct event device for your touchscreen
device = InputDevice('/dev/input/event3')

print(f"Listening for touch events on {device}")

# Loop to capture events
for event in device.read_loop():
    if event.type == ecodes.EV_ABS:
        absevent = categorize(event)
        if absevent.event.code == ecodes.ABS_MT_POSITION_X:
            print(f"X: {absevent.event.value}")
        elif absevent.event.code == ecodes.ABS_MT_POSITION_Y:
            print(f"Y: {absevent.event.value}")

