import time
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject
import time
import evdev
from evdev import InputDevice, categorize, ecodes
import threading

class TouchHandler:
    def __init__(self, fullscreenCB, normalCB, collapseCB, minTouchInterval=0.5):
        self.touchx = None
        self.touchy = None
        self.fullscreen_mode = False
        self.fullscreenCB = fullscreenCB
        self.normalCB = normalCB
        self.collapseCB = collapseCB
        self.last_touch = time.time()
        self.minTouchInterval = minTouchInterval
        self.drawingareas = []
        self.DA_positions = [(0, 0), (960, 0), (0, 540), (960, 540)]  # Position for each camera feed

        self._find_touchscreen_device()
        threading.Thread(target=self.get_touchscreen).start()
        
    def _find_touchscreen_device(self):
        devices = [InputDevice(path) for path in evdev.list_devices()]
        for device in devices:
            if "ILITEK" in device.name:  # Filter by device name
                self.touchscreen = device
                return
        self.touchscreen = None

    def get_touchscreen(self):
        print("Touchscreen thread started")
        if self.touchscreen:
            print(f"Touchscreen found: {self.touchscreen.path} ({self.touchscreen.name})")
            for event in self.touchscreen.read_loop():
                if event.type == ecodes.EV_ABS:
                    absevent = categorize(event)
                    if absevent.event.code == ecodes.ABS_X:
                        print(f"X: {absevent.event.value}")
                        self.touchx = absevent.event.value*1920/8192
                    elif absevent.event.code == ecodes.ABS_Y:
                        print(f"Y: {absevent.event.value}")
                        self.touchy = absevent.event.value*1080/8192
                        if time.time() - self.last_touch > self.minTouchInterval:
                            self.updateDA()
                            self.last_touch = time.time()
        else:
            print("No touchscreen device found.")
            
    def set_touch(self, touchx, touchy):
        self.touchx = touchx
        self.touchy = touchy
        self.updateDA()
        
    def updateDA(self):
        if self.touchx and self.touchy:
            if not self.fullscreen_mode:
                if self.touchx <= 960 and self.touchy <= 540:
                    sel_cam = 80
                elif self.touchx > 960 and self.touchy <= 540:
                    sel_cam = 85
                elif self.touchx <= 960 and self.touchy > 540:
                    sel_cam = 115
                elif self.touchx > 960 and self.touchy > 540:
                    sel_cam = 95
                
                GObject.idle_add(self.fullscreenCB, sel_cam) 
                self.fullscreen_mode = True
                for i in [80, 85, 115, 95]:
                        if i != sel_cam:
                            GObject.idle_add(self.collapseCB, i)
                print("here")
            else:  
                if self.touchx != 0 and self.touchy != 0:
                    for i in [80, 85, 115, 95]:
                        GObject.idle_add(self.normalCB, i)
                    self.fullscreen_mode = False
                    self.touchx = 0
                    self.touchy = 0


   
            