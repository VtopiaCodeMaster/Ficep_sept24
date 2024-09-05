
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GstVideo', '1.0')
from gi.repository import Gtk, GdkPixbuf

class GTKwindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Vtopia")
        self.set_default_size(1920,1080)  # Imposta la dimensione iniziale della finestra
        self.set_decorated(False)  # Rimuove la barra del titolo
        self.move(0, 0)
        self.connect("destroy", Gtk.main_quit)  # Collega il segnale destroy a Gtk.main_quit
        
        # Imposta il colore di sfondo su nero
        #self.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0, 0, 0, 1))
        
        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_size_request(640, 720)
        self.add(self.drawing_area)

        
        self.drawing_area.connect("realize", lambda w:self.on_realize(w, self.pipeline))

    def set_pipeline(self, pipeline):
        self.pipeline = pipeline

    def on_realize(self, widget, pipeline):
        window = widget.get_window()
        if window and pipeline:
            xid = window.get_xid()
            pipeline_sink=pipeline.get_by_name('camere_sink')
            if pipeline_sink:
                pipeline_sink.set_window_handle(xid)
                print("pipeline sink set to window handle", xid)
