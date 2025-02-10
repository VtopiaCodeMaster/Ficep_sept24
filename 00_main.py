import threading
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gst,GstVideo,GLib,GObject, Gtk
import time

import json
from Vlib.Gst.FrameBank import *
from Vlib.Gst.FBOutput import *
from Vlib.Gst.FBInput import *
from Vlib.SerialNumberChecks.SNChecker import SNChecker
from Vlib.Gst.PipeBlocks.NvGleSink import NvGleSink
from Vlib.Gst.PipeBlocks.Resize import Resize
from Vlib.Gtk.GstDrawingArea import GstDrawingArea
from Vlib.Gtk.UndecoratedWindow import UndecoratedWindow
from threading import Thread
from Window import Window
exit_flag = False

def extract_local_dict(json_file):
    with open(json_file, "r") as f:
        data = json.load(f)
    return data

def setupLocalInput(everyLocalUrl):
    localInput = {}
    for ip in everyLocalUrl:
        input = FBInput(type=FBInputType.safeH265,
                        name=ip,
                        addr=everyLocalUrl[ip],
                        path="/home/item/Ficep_sept24/Vlib/Gst/test/1280_720.png",
                        mode=RtspSrcMode.H265DECODE_DEFAULT)
        fb.addInput(input)
        localInput[ip] = input
    return localInput

def setupRemoteInput(everyRemoteUrl):
    remoteInput = {}
    for ip in everyRemoteUrl:
        input = FBInput(type=FBInputType.safeH265,
                        name=ip,
                        addr=everyRemoteUrl[ip],
                        path="/home/item/Ficep_sept24/Vlib/Gst/test/1280_720.png",
                        mode=RtspSrcMode.H265DECODE_DEFAULT)
        
        fb.addInput(input)
        remoteInput[ip] = input
   
    return remoteInput

def setupOutput(fps,localInput,remoteInput):
    outputs = {}
    for ipLoc,ipRem in zip(localInput,remoteInput):
        output = FBOutput(type = FBOutputType.streamSelector,
                            name=f"output{ipLoc}{ipRem}",
                            src = [ipLoc, ipRem],
                            fps = int(fps))
        outputs[f"output{ipLoc}{ipRem}"] = output
    return outputs
                      
def startPipes(win:Window):
    time.sleep(2)
    pipes=[]
    appsrcs=[]
    position=[(0,0),(960,0),(0,540),(960,540)]
    for output in outputs:
        appsrc = fb.getOutput(outputs[output])
        sink = NvGleSink(name=f"sink{output}")
        
        outFPS = FPSCounter(name=f"outFPS{output}", interval=2)
        sink.addCallback(PipeCallbackDescriptor(
            callback=outFPS.tick,
            elName=f"sink{output}",
            plug=PipeCallbackPlug.ON_PAD,
            plugName="sink"
        ))
        lsb=LiveStreamBuffer(name=f"lsb{output}", bufferSize=2)
        pipe = GstPipeRunner(appsrc.link(Resize(960,540)).link(lsb).link(sink))
        DA = GstDrawingArea(nvGleSink=sink, defaultSize=(960, 540), defaultPosition=position.pop(0))
        win.addGstDrawingArea(DA)
        pipes.append(pipe)
        appsrcs.append(appsrc)
        outFPS.printInThread()
    time.sleep(5)
    for pipe in pipes:
        pipe.start()

    for input in localInput:
        fb.acquire(localInput[input])
        time.sleep(1)
    for input in remoteInput:
        fb.acquire(remoteInput[input])
        time.sleep(1)
    for output in outputs:
        outputs[output].start()
    win.setupButton("Local", changeVisualization, (1820, 980))
    GLib.idle_add(win.show_all)

def changeVisualization(button):
    print("Button pressed")
    
    first_key = next(iter(outputs))
    
    # Check if that first output is "1"
    if outputs[first_key].outStream == 1:
        # If so, set them ALL to 0
        for key in outputs:
            outputs[key].outStream = 0
    else:
        # Otherwise, set them ALL to 1
        for key in outputs:
            outputs[key].outStream = 1

SNc = SNChecker(folderToClear="/home/item/Ficep_sept24",
              SNpath="/home/item/glibc-2.28/benchtests/strcoll-inputs/SN.txt")
SNc.check()

jsonDict = extract_local_dict("/home/item/Ficep_sept24/config.json")
everyLocalUrl = jsonDict["local"]
everyRemoteUrl = jsonDict["remote"]
fps=jsonDict["fps"]
Gst.init(None)
fb = FrameBank()
localInput=setupLocalInput(everyLocalUrl)
remoteInput=setupRemoteInput(everyRemoteUrl)
outputs=setupOutput(fps,localInput,remoteInput)

win = Window("Basic Rtsp Pipe", defaultSize=(1920, 1080), defaultPosition=(0, 0))
win.start()
setupThread = Thread(target=startPipes, args=(win,), daemon=True)
setupThread.start()
Gtk.main()
