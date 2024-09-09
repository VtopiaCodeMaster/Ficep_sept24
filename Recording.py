import gi
gi.require_version("Gst", "1.0")
gi.require_version("GstRtsp", "1.0")
from gi.repository import Gst, GLib
import time


class Recording:
    def __init__(self,cam_ip):
        self.cam_ip = cam_ip
        self.url=f"rtsp://192.168.3.{self.cam_ip}:554/stream1"
        self.createPipeline()
    
    def createPipeline(self):
        self.pipeline = Gst.parse_launch(
                f"rtspsrc latency=10 buffer-mode=none drop-on-latency=true do-retransmission=false udp-buffer-size=212000 location={self.url} name=src ! "
                f"rtph265depay ! h265parse config-interval=-1 ! nvv4l2decoder ! "
                f"queue max-size-time=30000000000 leaky=downstream ! nvv4l2h265enc ! h265parse ! " 
                f"tee name=tee "
                f"tee. ! valve name=valve_save drop=true ! filesink location=/home/item/Recordings/vid.mp4 name=filesink"
                f"tee. ! valve name=valve_fake drop=false ! video/x-h265, stream-format=(string)byte-stream ! fakesink"
            )
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        #self.bus.connect("message", self.on_message)
        return self.pipeline
    
    def start(self):
        self.pipeline.set_state(Gst.State.PLAYING)
        try:
            loop = GLib.MainLoop()
            loop.run()
        except KeyboardInterrupt:
            loop.quit()
    
    def stop(self):
        self.pipeline.set_state(Gst.State.NULL)
    
    def start_rec(self):
        self.pipeline.get_by_name("valve_save").set_property("drop", False)
        self.pipeline.get_by_name("valve_fake").set_property("drop", True)
    
    def stop_rec(self):
        self.pipeline.get_by_name("valve_save").set_property("drop", True)
        self.pipeline.get_by_name("valve_fake").set_property("drop", False)

Gst.init(None)
cam_recording = Recording(80)
cam_recording.start()
time.sleep(30)
cam_recording.start_rec()
time.sleep(30)
cam_recording.stop_rec()
