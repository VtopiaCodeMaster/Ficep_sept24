import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstRtsp', '1.0')
from gi.repository import Gst, GLib
import time
from TilerIF import *
import socket
from urllib.parse import urlparse
from TilerIF import *
from ValveIF import *

class PipelineGST:
    def __init__(self):
        self.rtspConfig = "latency=10"#50 buffer-mode=none drop-on-latency=true do-retransmission=false udp-buffer-size=212000"
        self.queueConfig = "max-size-buffers=10 leaky=downstream"# max-size-bytes=0 max-size-time=0"
        self.decodePipe = f"rtph265depay ! h265parse config-interval=-1 ! nvv4l2decoder ! queue {self.queueConfig}"#disable-dpb=true
        self.glePipe = "nvegltransform ! nveglglessink sync=false force-aspect-ratio=false qos=0"
        self.muxConfig = "live-source=1"

        self.stream_IP = [80, 85, 90, 95]
        self.main_url = {}
        self.backup_img = {}
        self.stream_paths = {}
        self.main_url_set = False
        self.decIndex={80:'0', 85:'1', 90:'2', 95:'3'}
        self.faultCam=[]
        for cam in self.stream_IP:
            self.faultCam.append(f"filesrc location=/home/item/Ficep_sept24/Fault{cam}.png ! pngdec ! imagefreeze ! nvvidconv ! video/x-raw(memory:NVMM), format=(string)NV12, framerate=25/1 ! queue {self.queueConfig} ! nvvidconv")

        Gst.init(None)

    def set_main_urls(self, s80, s85, s90, s95):
        self.main_url[80] = s80
        self.main_url[85] = s85
        self.main_url[90] = s90
        self.main_url[95] = s95
        for ip in self.stream_IP:
            self.stream_paths[ip] = f"rtspsrc {self.rtspConfig} location={self.main_url[ip]} ! {self.decodePipe}"
            
        self.main_url_set = True

    def _check_rtsp_source(self, url):
        parsed_url = urlparse(url)
        host = parsed_url.hostname
        port = parsed_url.port if parsed_url.port else 554  # Default RTSP port is 554

        # Create a socket to check the connection
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)  # Set timeout to 2 seconds
            try:
                s.connect((host, port))
                return True
            except (socket.timeout, socket.error):
                print(f"WAR: RTSP source {url} is not available.")
                return False


    def setupDeepStream(self):
        if not self.main_url_set:
            print("Stream paths not set")
            return

        
        self.pipeline_camere = Gst.parse_launch(
        f"{self.stream_paths[80]} name=cam_80 ! valve name=valve_80 ! mux_0.sink_0 "
        f"{self.faultCam[0]} ! valve name=valve_f80 drop=True ! mux_0.sink_1 "
        f"nvstreammux name=mux_0 width=1280 height=720 batch-size=1 {self.muxConfig} ! queue {self.queueConfig} ! valve name=valve_sel80 ! mux_til.sink_0 "
        
        f"{self.stream_paths[85]} name=cam_85 ! valve name=valve_85 ! mux_1.sink_0 "
        f"{self.faultCam[1]} ! valve name=valve_f85 drop=True ! mux_1.sink_1 "
        f"nvstreammux name=mux_1 width=1280 height=720 batch-size=1 {self.muxConfig} ! queue {self.queueConfig} ! valve name=valve_sel85 ! mux_til.sink_1 "

        f"{self.stream_paths[90]} name=cam_90 ! valve name=valve_90 ! mux_2.sink_0 "
        f"{self.faultCam[2]} ! valve name=valve_f90 drop=True ! mux_2.sink_1 "
        f"nvstreammux name=mux_2 width=1280 height=720 batch-size=1 {self.muxConfig} ! queue {self.queueConfig} ! valve name=valve_sel90 ! mux_til.sink_2 "

        f"{self.stream_paths[95]} name=cam_95 ! valve name=valve_95 ! mux_3.sink_0 "
        f"{self.faultCam[3]} ! valve name=valve_f95 drop=True ! mux_3.sink_1 "
        f"nvstreammux name=mux_3 width=1280 height=720 batch-size=1 {self.muxConfig} ! queue {self.queueConfig} ! valve name=valve_sel95 ! mux_til.sink_3 "

        f"nvstreammux name=mux_til width=1280 height=720 batch-size=4 {self.muxConfig} ! queue {self.queueConfig} ! "
        f"nvmultistreamtiler rows=2 columns=2 ! "
        f"{self.glePipe} name=camere_sink "
        )
        self.pipeline_camere.set_name("camere")
        return self.pipeline_camere

        
    def add_items(self, pm=False):
        #TilerIF TBD
        self.tilerIF = TilerIF(self.pipeline_camere, "nvtiler")

        valve_names=[]
        valve_faultNames=[]
        valve_mainMux=[]
        for ip in self.stream_IP:
            valve_faultNames.append(self.pipeline_camere.get_by_name(f"valve_f{ip}"))
            valve_names.append(self.pipeline_camere.get_by_name(f"valve_{ip}"))
            valve_mainMux.append(self.pipeline_camere.get_by_name(f"valve_sel{ip}"))
            
        self.valveIF=ValveIF(valve_names,valve_faultNames,valve_mainMux)

        pass

    
    def _onMessage(self, bus, msg, pipeline):
        if msg.type == Gst.MessageType.ERROR:
            err, debug = msg.parse_error()
            print("Error received from element %s of pipeline %s: %s" % (msg.src.get_name(), pipeline.get_name(), err), debug)
            #self.restart_pipeline(pipeline.get_name())
        elif msg.type == Gst.MessageType.STATE_CHANGED:
            pass

    def run(self):
        self.pipeline_camere.set_state(Gst.State.PLAYING)
        bus = self.pipeline_camere.get_bus()
        bus.add_signal_watch()
        bus.connect("message", lambda bus, msg: self._onMessage(bus, msg, "camere"))
        try:
            loop = GLib.MainLoop()

            loop.run()
        except KeyboardInterrupt:
            loop.quit()


    def stop(self):
        self.pipeline_camere.set_state(Gst.State.NULL)
        print("pipeline stopped")


