import time
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject
import time


class TouchHandler:
    def __init__(self,drawingareas):
        self.touchx = None
        self.touchy = None
        self.fullscreen_mode = False
        self.drawingareas = []
        for key in drawingareas:
            self.drawingareas.append(drawingareas[key])
            
    def get_touch(self, touchx, touchy):
        self.touchx = touchx
        self.touchy = touchy
        self.updateDA()
        
    def updateDA(self):
        if not self.fullscreen_mode:
            if self.touchx <= 960 and self.touchy <= 540:
                print("1")
                self.update_ui(self.drawingareas[0], 1920, 1080)
                self.fullscreen_mode = True
                drawingarea_on = self.drawingareas[0]

            elif self.touchx > 960 and self.touchy <= 540:
                self.update_ui(self.drawingareas[1], 1920, 1080)
                self.fullscreen_mode = True
                drawingarea_on = self.drawingareas[1]

            elif self.touchx <= 960 and self.touchy > 540:
                self.update_ui(self.drawingareas[2], 1920, 1080)
                self.fullscreen_mode = True
                drawingarea_on = self.drawingareas[2]
                
            elif self.touchx > 960 and self.touchy > 540:
                self.update_ui(self.drawingareas[3], 1920, 1080)
                self.fullscreen_mode = True
                drawingarea_on = self.drawingareas[3]
                
            for drawingarea in self.drawingareas:
                    if drawingarea != drawingarea_on:
                        self.update_ui(drawingarea, 1, 1)
            print("here")
        else:  
            if self.touchx != 0 and self.touchy != 0:
                for drawingarea in self.drawingareas:
                    self.update_ui(drawingarea, 960, 540)
                self.fullscreen_mode = False
                self.touchx = 0
                self.touchy = 0
        
        

    def _set_size(self, widget, width, height):
        widget.set_size_request(width, height)
        time.sleep(0.01)  # simulate setting delay
        widget.queue_draw_area(0, 0, width, height)

    def update_ui(self,widget, width, height):
        GObject.idle_add(self._set_size, widget, width, height)

   
            