import threading
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0')
from gi.repository import Gst, GstVideo
import signal
import subprocess
from GTKwindow import *
from Pipeline import *
from HandlerFault import *
from Recorder import *
from TouchHandler import *
from HttpsDownloader import HttpPoller
from HttpsDownloader import HttpPoller
from Vlib.VtopiaSWUpdate.InternetConnectionChecker import InternetConnectionChecker
from Vlib.VtopiaSWUpdate.VersionComparer import *
exit_flag = False

def signal_handler(sig, frame):
    exit_flag = True
    HandlerFault_thread.join()
    
    Gtk.main_quit()

signal.signal(signal.SIGINT, signal_handler)

#new version evviva

Gst.init(None)

every_ip=[50,51,52,53]
everyUrl={}
for ip in every_ip:
    everyUrl[ip]=f"rtsp://172.16.5.{ip}:554/stream1"
win = GTKwindow(every_ip)


pipelines={}
pipes={}
HandlersFault_dict={}
workingIp=[]
workingUrl={}
for ip in every_ip:
    pipes[ip]=Pipeline(ip,everyUrl[ip])
    pipelines[ip] = pipes[ip].createPipeline()
    if pipes[ip].workingIp():
        workingIp.append(ip)
        workingUrl[ip]=everyUrl[ip]
        HandlersFault_dict[ip]=HandlerFault(pipelines[ip], ip)
print("Working Ip: ", workingIp)

win.set_pipelines(pipelines)

win.show_all()
win.hide_cursor()
win.connect_drawing_area()
HttpThread = threading.Thread(target=HttpPoller, args=(workingIp, workingUrl))
for ip in every_ip:
    Cam_thread=threading.Thread(target=pipes[ip].start).start()
for ip in workingIp:
    HandlerFault_thread=threading.Thread(target=HandlersFault_dict[ip].pipeline_started).start()
HttpThread.start()
print("Setup finished, feeding data")

Gtk.main()


