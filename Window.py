from Vlib.Gtk.UndecoratedWindow import UndecoratedWindow
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

class Window(UndecoratedWindow):
    def __init__(self, title="My Window", defaultSize=(800, 600), defaultPosition=(100, 100)):
        super().__init__(title=title, defaultSize=defaultSize, defaultPosition=defaultPosition)
        self.set_default_size(*defaultSize)
        self.move(*defaultPosition)
        self.set_border_width(10)

        self.box = self._box  
        
        self.overlay = Gtk.Overlay()
        self.box.put(self.overlay, 0, 0)

        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_size_request(*defaultSize)
        self.overlay.add(self.drawing_area)

        self.DA_positions = [
            (0, 0),
            (960, 0),
            (0, 540),
            (960, 540)
        ]
        
        self.drawing_areas = []

        self.fullscreen_DA = None  

        self.button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.overlay.add_overlay(self.button_box)

    def addGstDrawingArea(self, drawingArea):
        GLib.idle_add(self.box.put, drawingArea, *drawingArea._position)
        GLib.idle_add(self.ensure_overlay_on_top)

        self.drawing_areas.append(drawingArea)

        def move(position=None, DA=drawingArea):
            GLib.idle_add(self.box.move, DA, *position)

        drawingArea.moveCallback = move

        drawingArea.add_events(
            Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.TOUCH_MASK
        )
        drawingArea.connect("button-press-event", self.on_drawingarea_press)

    def on_drawingarea_press(self, widget, event):
        if self.fullscreen_DA == widget:
            self.normalDA()
        else:
            self.fullscreenDA(widget)
        return True 

    def fullscreenDA(self, drawing_area):
        if drawing_area not in self.drawing_areas:
            return

        if self.fullscreen_DA:
            self.normalDA()

        print("Setting a DrawingArea to fullscreen")
        drawing_area.set_size_request(1920, 1080)
        self.box.move(drawing_area, 0, 0)
        drawing_area.queue_draw()

        self.fullscreen_DA = drawing_area

        # Collapse other drawing areas
        for da in self.drawing_areas:
            if da != drawing_area:
                self.collapseDA(da)

    def normalDA(self):
        if not self.fullscreen_DA:
            return

        print("Restoring all DrawingAreas to normal layout")
        for i, da in enumerate(self.drawing_areas):
            x, y = self.DA_positions[i]
            da.set_size_request(960, 540)
            self.box.move(da, x, y)
            da.queue_draw()

        self.fullscreen_DA = None

    def collapseDA(self, drawing_area):
        if drawing_area in self.drawing_areas:
            print("Collapsing a DrawingArea")
            drawing_area.set_size_request(0, 0)
            drawing_area.queue_draw()

    def ensure_overlay_on_top(self):
        if self.overlay.get_parent() is not None:
            self.box.remove(self.overlay)
            self.box.put(self.overlay, 0, 0)
            self.overlay.show_all()

    def addButton(self, button, position):
        """Place the button inside the overlay box at (x,y)."""
        self.button_box.pack_start(button, False, False, 0)
        self.button_box.set_halign(Gtk.Align.START)
        self.button_box.set_valign(Gtk.Align.START)
        self.button_box.set_margin_top(position[1])
        self.button_box.set_margin_start(position[0])

        # Ensure it's on top
        self.ensure_overlay_on_top()
        return button

    def setupButton(self, label, callback, position):
        """Creates a button, connects its callback, and adds it to the overlay."""
        button = Gtk.Button(label=label)
        # Allow the button to receive mouse/touch events explicitly
        button.add_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.TOUCH_MASK)

        button.connect("clicked", callback)
        self.addButton(button, position)
        self.show_all()
        

    def quit_app(self, button):
        """Close the GTK main loop."""
        Gtk.main_quit()
