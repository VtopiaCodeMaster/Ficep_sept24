import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
import time
from threading import *

class HandlerFault:
    def __init__(self, pipeline, ip):
        self.pipeline = pipeline
        self.ip=ip
        self.element_name = f"cam_{self.ip}"
        self.valveFault = self.pipeline.get_by_name(f"valve_f{self.ip}")
        self.valve = self.pipeline.get_by_name(f"valve_{self.ip}")
        self.fps = 0
        self.frame_count = 0
        self.interval = 5
        self.black_screen_on = False
        
        element = self.pipeline.get_by_name(self.element_name)
        if not element:
            raise ValueError(f"Element with name {self.element_name} not found in pipeline.")
        
        self.src_pad = element.get_static_pad('src')
        if not self.src_pad:
            raise ValueError(f"Source pad not found on element {self.element_name}.")
        else:
            print(f"Source pad found on element {self.element_name}.")
            self.attach_probe()
        

    def attach_probe(self):
        # Attach a buffer probe to count frames
        self.src_pad.add_probe(Gst.PadProbeType.BUFFER, self.probe_callback, None)

    def probe_callback(self, pad, info, user_data):
        self.frame_count += 1
        return Gst.PadProbeReturn.OK

    def start_timer(self):
        self.timer = Timer(self.interval, self.report_fps)
        self.timer.start()
    
    def show_fault(self):
        self.valveFault.set_property("drop", False)
        self.valve.set_property("drop", True)
        
    def show_source(self):
        self.valveFault.set_property("drop", True)
        self.valve.set_property("drop", False)
        
    def report_fps(self):
        # Calculate and report FPS
        current_time = time.time()
        elapsed = current_time - self.start_time
        if elapsed > 0:
            self.fps = self.frame_count / elapsed
            #print(f'{self.element_name} FPS: {self.fps}')
        
        if self.fps < 5 and not self.black_screen_on:
            self.show_fault()
            self.black_screen_on = True
        elif self.fps > 5 and self.black_screen_on:
            self.show_source()
            self.black_screen_on = False
        
        self.frame_count = 0
        self.start_time = current_time
        self.start_timer()  # Restart the timer for the next report

    def FpsRet(self,source_index):
        self.source_index=source_index
        return self.fps
    
    def stop(self):
        # Cancel the timer if it is still running
        if self.timer:
            self.timer.cancel()
    
   
    def pipeline_started(self):
        self.start_time = time.time()
        self.frame_count = 0
        self.start_timer()