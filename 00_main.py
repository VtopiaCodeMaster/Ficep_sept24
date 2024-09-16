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
from SaveRec import *
exit_flag = False
def signal_handler(sig, frame):
    exit_flag = True
    HandlerFault_thread.join()
    
    Gtk.main_quit()
    
#da implementare il touch, funzione provvisoria per test, le coordinate touch vanno inviate a resize_drawing_area
def test_touch_resize():
    time.sleep(5)
    win.resize_drawing_area(100,300)
    time.sleep(5)
    win.resize_drawing_area(200,400)
    print("ciao")
    time.sleep(3)

def rec_setup(ip):
    rec=Recorder(ip)
    rec.setup_pipeline()
    threading.Thread(target=rec.start_pipeline).start()
    time.sleep(10)
    rec.on_request()
    time.sleep(15)
    rec.on_request()
    

    
    

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
'''recording = Recorder(80)
recording.createPipeline()'''
for ip in every_ip:
    Cam_thread=threading.Thread(target=pipes[ip].start).start()
    HandlerFault_thread=threading.Thread(target=HandlersFault_dict[ip].pipeline_started).start()

threading.Thread(target=rec_setup,args=(every_ip[0],)).start()
threading.Thread(target=rec_setup,args=(every_ip[1],)).start()
threading.Thread(target=rec_setup,args=(every_ip[2],)).start()
threading.Thread(target=rec_setup,args=(every_ip[3],)).start()
#threading.Thread(target=test_touch_resize).start()
print("Setup finished, feeding data")

Gtk.main()


