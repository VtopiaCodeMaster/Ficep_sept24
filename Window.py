from Vlib.Gtk.UndecoratedWindow import UndecoratedWindow
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, GObject

class Window(UndecoratedWindow):
    def __init__(self, title="My Window", defaultSize=(800, 600), defaultPosition=(100, 100)):
        super().__init__(title=title, defaultSize=defaultSize, defaultPosition=defaultPosition)
        self.set_default_size(*defaultSize)
        self.move(*defaultPosition)
        self.set_border_width(10)

        # Create an overlay and add it into the fixed container (self._box)
        self.overlay = Gtk.Overlay()
        self._box.put(self.overlay, 0, 0)

        # A background drawing area added as the main child of the overlay
        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_size_request(*defaultSize)
        self.overlay.add(self.drawing_area)

        # Create a button container that will be overlaid on top of the drawing area
        self.button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.overlay.add_overlay(self.button_box)

        
    def addButton(self, button, position):
        """Adds a button into the overlay's button box and positions it."""
        self.button_box.pack_start(button, False, False, 0)
        # Position the button_box using margins for a rough offset.
        self.button_box.set_halign(Gtk.Align.START)
        self.button_box.set_valign(Gtk.Align.START)
        self.button_box.set_margin_top(position[1])
        self.button_box.set_margin_start(position[0])
        return button

    def setupButton(self, label, callback, position):
        """Creates a button, connects its callback, and adds it to the overlay."""
        button = Gtk.Button(label=label)
        button.connect("clicked", callback)
        self.addButton(button, position)
        return button

    def change(self, button,outputs):
        for output in outputs:
            outputs[output].outStream=1
        

    def quit_app(self, button):
        Gtk.main_quit()

    def addGstDrawingArea(self, drawingArea):
        """
        Adds a GstDrawingArea (assumed to have a _position attribute) into the fixed container
        and then ensures that the overlay is re‑added (thus on top).
        """
        # Add the drawing area into the fixed container at its specified position.
        GLib.idle_add(self._box.put, drawingArea, *drawingArea._position)
        # After adding the drawing area, re-add the overlay to force it on top.
        GLib.idle_add(self.ensure_overlay_on_top)
        # Optionally remember the drawing area.
        self._GstDrawingAreas.append(drawingArea)
        # Set up a move callback so that the drawing area can be moved later.
        def move(position=None, DA=drawingArea, box=self._box):
            GLib.idle_add(box.move, DA, *position)
        drawingArea.moveCallback = move

    def ensure_overlay_on_top(self):
        """
        Remove and re-add the overlay in the fixed container so it becomes the topmost widget.
        """
        # Check if the overlay is still a child of self._box.
        if self.overlay.get_parent() is not None:
            self._box.remove(self.overlay)
            self._box.put(self.overlay, 0, 0)
            self.overlay.show_all()
