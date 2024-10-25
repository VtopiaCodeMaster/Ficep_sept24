import gi

gi.require_version("Gtk", "3.0")
gi.require_version("GstVideo", "1.0")
from gi.repository import Gtk, Gdk
from TouchHandler import *

class GTKwindow(Gtk.Window):
    def __init__(self,every_ip):
        super().__init__(title="Vtopia")
        self.every_ip=every_ip
        self.set_default_size(1920, 1080)  # Imposta la dimensione iniziale della finestra
        self.DA_positions = [(0, 0), (960, 0), (0, 540), (960, 540)]  # Position for each camera feed
        self.set_decorated(False)  # Rimuove la barra del titolo
        self.set_keep_above(True) 
        self.move(0, 0)
        self.connect(
            "destroy", Gtk.main_quit
        )  # Collega il segnale destroy a Gtk.main_quit
        self.box = Gtk.Fixed()
        self.add(self.box)
        #self.set_keep_below(True)
        self.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0, 0, 0, 1))
        self.box.set_redraw_on_allocate(False)
        # Imposta il colore di sfondo su nero
        # self.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0, 0, 0, 1))
        self.set_drawing_area()
        self.touchHandler = TouchHandler(self.set_DA_fullScreen, self.set_DA_normal, self.set_DA_collapse, self.every_ip)


    def set_pipelines(self, pipelines):
        self.pipelines = pipelines
        
        self.sinks={}
        

    def set_drawing_area(self):
        self.drawing_areas = {}
        for index, ip in enumerate(self.every_ip):
            self.drawing_areas[ip] = Gtk.DrawingArea()
            self.drawing_areas[ip].set_size_request(960, 540)  # Set size of each camera feed
            x, y = self.DA_positions[index]
            self.box.put(self.drawing_areas[ip], x, y)  # Place each camera feed at specified position

    def get_drawing_area(self):
        return self.drawing_areas
        
    def connect_drawing_area(self):
        for ip in self.every_ip:
            self.on_realize(self.drawing_areas[ip], self.pipelines[ip], f"sink_{ip}")
            
    def resize_drawing_area(self,height,width):
        self.touchHandler.get_touch(height, width)

    def on_realize(self, widget, pipeline, sink_name):
        window = widget.get_window()
        if window and pipeline:
            xid = window.get_xid()
            pipeline_sink=pipeline.get_by_name(sink_name)
            if pipeline_sink:
                pipeline_sink.set_window_handle(xid)
                print("pipeline sink set to window handle", xid)

    def set_DA_fullScreen(self, ip):
        self.drawing_areas[ip].set_size_request(1920, 1080)
        self.box.move(self.drawing_areas[ip], 0, 0)

    def set_DA_normal(self, ip):
        x, y = self.DA_positions[self.every_ip.index(ip)]
        self.drawing_areas[ip].set_size_request(960, 540)
        self.box.move(self.drawing_areas[ip], x, y)

    def set_DA_collapse(self, ip):
        self.drawing_areas[ip].set_size_request(0, 0)
    
    def hide_cursor(window):
        invisible_cursor = Gdk.Cursor.new(Gdk.CursorType.BLANK_CURSOR)
        window.get_window().set_cursor(invisible_cursor)