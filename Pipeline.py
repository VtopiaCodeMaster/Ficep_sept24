import gi

import socket
gi.require_version("Gst", "1.0")
gi.require_version("GstRtsp", "1.0")
from gi.repository import Gst, GLib
from urllib.parse import urlparse

class Pipeline:
    def __init__(self,ip,url):
        self.ip = ip
        self.url=url
        self.rtspConfig = "latency=10 buffer-mode=none drop-on-latency=true do-retransmission=false udp-buffer-size=212000"
        self.queueConfig = (
            "max-size-bytes=30000000000 leaky=downstream"  # max-size-bytes=0 max-size-time=0"
        )
        self.decodePipe = f"rtph265depay ! h265parse config-interval=-1 ! nvv4l2decoder ! queue {self.queueConfig}"  # disable-dpb=true
        self.glePipe = (
            "nvegltransform ! nveglglessink sync=true force-aspect-ratio=false qos=0"
        )
        self.muxConfig = "live-source=1"
        self.faultCam = f"filesrc location=/home/item/Ficep_sept24/Fault{self.ip}.png ! pngdec ! imagefreeze ! nvvidconv ! video/x-raw(memory:NVMM), format=(string)NV12, framerate=25/1 ! queue {self.queueConfig} ! nvvidconv"
        
        if self.checkRtspsrc():
            self.streamPath = f"rtspsrc {self.rtspConfig} location={self.url} ! {self.decodePipe}"
            self.path=f"{self.streamPath} name=cam_{self.ip} ! valve name=valve_{self.ip} ! mux_0.sink_0 {self.faultCam} ! valve name=valve_f{self.ip} drop=True ! mux_0.sink_1 nvstreammux name=mux_0 width=1280 height=720 batch-size=1 num-surfaces-per-frame=1 {self.muxConfig}"
        else:
            self.path = f"filesrc location=/home/item/Ficep_sept24/Fault{self.ip}.png ! pngdec ! imagefreeze ! nvvidconv ! video/x-raw(memory:NVMM), format=(string)NV12, framerate=25/1 ! queue {self.queueConfig} ! nvvidconv"

        

    def _onMessage(self, bus, msg):
        if msg.type == Gst.MessageType.ERROR:
            err, debug = msg.parse_error()
            print(
                "Error received from element %s: %s"
                % (msg.src.get_name(), err),
                debug,
            )
        elif msg.type == Gst.MessageType.STATE_CHANGED:
            pass
    
    def workingIp(self):
        if self.checkRtspsrc():
            return True
        
    def checkRtspsrc(self):
        parsed_url = urlparse(self.url)
        host = parsed_url.hostname
        port = parsed_url.port if parsed_url.port else 554  # Default RTSP port is 554

        # Create a socket to check the connection
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)  # Set timeout to 2 seconds
            try:
                s.connect((host, port))
                return True
            except (socket.timeout, socket.error):
                print(f"WAR: RTSP source {self.url} is not available.")
                return False
            
    def createPipeline(self):
        self.pipeline = Gst.parse_launch(
            f"{self.path} ! queue {self.queueConfig} ! "
            f"{self.glePipe} name=sink_{self.ip} "
        )
        return self.pipeline
    
    def start(self):
        self.pipeline.set_state(Gst.State.PLAYING)
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self._onMessage)
        bus.connect("message::eos", self.on_eos)
        bus.connect("message::error", self.on_error)
        try:
            loop = GLib.MainLoop()
            loop.run()
        except KeyboardInterrupt:
            loop.quit()
    
    def on_eos(self, bus, msg):
        print("End-of-stream")
        self.pipeline.set_state(Gst.State.NULL)

    def on_error(self, bus, msg):
        err, debug = msg.parse_error()
        print(f"Error: {err}, {debug}")
        self.pipeline.set_state(Gst.State.NULL)

    
    
