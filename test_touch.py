import evdev
from evdev import InputDevice, categorize, ecodes
#takes effect after reboot, works!
#sudo usermod -aG input item

# Replace '/dev/input/eventX' with the correct event device for your touchscreen

# List all available input devices
'''devices = [InputDevice(path) for path in evdev.list_devices()]
for device in devices:
    print(f"Device: {device.path}, Name: {device.name}")
    print(f"Capabilities: {device.capabilities(verbose=True)}")
    print("-" * 40)'''



def find_touchscreen_device():
    devices = [InputDevice(path) for path in evdev.list_devices()]
    for device in devices:
        if "ILITEK" in device.name:  # Filter by device name
            return device
    return None

# Auto-detect the touchscreen device
touchscreen = find_touchscreen_device()

if touchscreen:
    print(f"Touchscreen found: {touchscreen.path} ({touchscreen.name})")
    for event in touchscreen.read_loop():
        if event.type == ecodes.EV_ABS:
            absevent = categorize(event)
            if absevent.event.code == ecodes.ABS_MT_POSITION_X:
                print(f"X: {absevent.event.value}")
            elif absevent.event.code == ecodes.ABS_MT_POSITION_Y:
                print(f"Y: {absevent.event.value}")
else:
    print("No touchscreen device found.")
