import threading
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0')
from gi.repository import Gst, GstVideo
import time
import depthai as dai
import signal
from GTKwindow import *
import argparse
from Pipeline import *
from HandlerFault import *
from TouchHandler import *

exit_flag = False
def signal_handler(sig, frame):
    exit_flag = True
    HandlerFault_thread.join()
    
    Gtk.main_quit()

signal.signal(signal.SIGINT, signal_handler)


Gst.init(None)

every_ip=[80,85,115,95]
win = GTKwindow(every_ip)


pipelines={}
pipes={}
HandlersFault_dict={}
for ip in every_ip:
    pipes[ip]=Pipeline(ip)
    pipelines[ip] = pipes[ip].createPipeline()
    HandlersFault_dict[ip]=HandlerFault(pipelines[ip], ip)

win.set_pipelines(pipelines)

win.show_all()
win.connect_drawing_area()

for ip in every_ip:
    Cam_thread=threading.Thread(target=pipes[ip].start).start()
    HandlerFault_thread=threading.Thread(target=HandlersFault_dict[ip].pipeline_started).start()

print("Setup finished, feeding data")

Gtk.main()


