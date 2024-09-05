import threading
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0')
from gi.repository import Gst, GstVideo
from pipelineGST import * 
import time
import depthai as dai
import signal
from GTKwindow import *
import argparse



exit_flag = False
def signal_handler(sig, frame):
    exit_flag = True
    pipelineGST.stop()


signal.signal(signal.SIGINT, signal_handler)


Gst.init(None)


win = GTKwindow()

pipelineGST = PipelineGST()
pipelineGST.set_main_urls(
    "rtsp://192.168.3.115:554/stream1",  # 
    "rtsp://192.168.3.85:554/stream1",  # 
    "rtsp://192.168.3.90:554/stream1",  # 
    "rtsp://192.168.3.95:554/stream1",  # 
)
pipe = pipelineGST.setupDeepStream()

win.set_pipeline(pipe)
win.show_all()

pipelineGST.run()
print("Setup finished, feeding data")

Gtk.main()

