import threading
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gst,GstVideo,GLib,GObject, Gtk
import time
from zipfile import ZipFile
from functools import partial
import os
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
from Vlib.http.HttpGETServer import HttpGETServer
from SetupRecording import SetupRecording
from Vlib.Startup_logging.SafeCallbackWrapper import safe_callback

exit_flag = False

def extract_local_dict(json_file):
    with open(json_file, "r") as f:
        data = json.load(f)
    return data

def setupLocalInput(everyLocalUrl, fb):
    localInput = {}
    for ip, i in zip(everyLocalUrl, range(50, 54)):
        input = FBInput(type=FBInputType.safeH265,
                        name=ip,
                        addr=everyLocalUrl[ip],
                        path=f"/home/item/Ficep_sept24/Data/Fault{i}.png",
                        mode=RtspSrcMode.H265DECODE_DEFAULT)
        fb.addInput(input)
        localInput[ip] = input
    return localInput


def setupOutput(fps,localInput):
    outputs = {}
    for ipLoc in localInput:
        output = FBOutput(type = FBOutputType.streamSelector,
                            name=f"output{ipLoc}",
                            src = [ipLoc],
                            fps = int(fps))
        outputs[f"output{ipLoc}"] = output
    return outputs
                      
def startPipes(win:Window, outputs, fb, localInput):
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
        lsb=LiveStreamBuffer(name=f"lsb{output}", bufferSize=8)
        pipe = GstPipeRunner(appsrc.link(Resize(960,540)).link(lsb).link(sink))
        DA = GstDrawingArea(nvGleSink=sink, defaultSize=(960, 540), defaultPosition=position.pop(0))
        GLib.idle_add(safe_callback(win.addGstDrawingArea), DA)
        pipes.append(pipe)
        appsrcs.append(appsrc)
        outFPS.printInThread()
    time.sleep(5)
    for pipe in pipes:
        pipe.start()

    for input in localInput:
        fb.acquire(localInput[input])
        time.sleep(1)
    for output in outputs:
        outputs[output].start()
    GLib.idle_add(safe_callback(win.show_all))
    GLib.idle_add(safe_callback(lambda: win.go_fullscreen(window=win)))
    GLib.idle_add(safe_callback(win.setAsForeground))

def setupRecording(localUrls: Dict[str, str],fps):
    listUrls = list(localUrls.values())
    recorder=SetupRecording(urls=listUrls,destinationFolder="/home/item/Recordings",ips=list(localUrls.keys()),fps=int(fps),preTime=30)
    return recorder

def httpServerSetup(everyLocalUrl,ipMonitor,fps):
    recorder = setupRecording(everyLocalUrl,fps)
    wrapped_callback = partial(saveBufferZip, recorder)
    httpServer = HttpGETServer(pathFileToBeDownloaded=['/home/item/Recordings.zip'],callback=[wrapped_callback],downloadRule=["/recordings"],port=8080,host=ipMonitor)
    httpServer.startInThread()

def saveBufferZip(recorder):
    recorder.saveBuffer()
    pathFolderToBeZip = "/home/item/Recordings"
    pathZip = "/home/item/Recordings.zip"
    with ZipFile(pathZip, 'w') as zipObj:
        for folderName, subfolders, filenames in os.walk(pathFolderToBeZip):
            for filename in filenames:
                filePath = os.path.join(folderName, filename)
                zipObj.write(filePath, os.path.relpath(filePath, pathFolderToBeZip))
    #Clean Recordings folder of its file maintaining the folder and delete zip file
    for folderName, subfolders, filenames in os.walk(pathFolderToBeZip):
        for filename in filenames:
            filePath = os.path.join(folderName, filename)
            os.remove(filePath)
    
def main():
    global outputs
    global win
    global fb
    global fps    
    SNc = SNChecker(folderToClear="/home/item/FicepDualMonitor",
                SNpath="/home/item/glibc-2.28/benchtests/strcoll-inputs/SN.txt")
    SNc.check()

    jsonDict = extract_local_dict("/home/item/Ficep_sept24/config.json")
    everyLocalUrl = jsonDict["local"]
    fps=jsonDict["fps"]
    ipMonitor = jsonDict["monitor"]["ip"]
    Gst.init(None)
    fb = FrameBank()
    localInput=setupLocalInput(everyLocalUrl,fb)
    outputs=setupOutput(fps,localInput)

    win = Window("Basic Rtsp Pipe", defaultSize=(1920, 1080), defaultPosition=(0, 0))
    win.start()
    win.setAsBackground()
    setupThread = Thread(target=startPipes, args=(win,outputs,fb,localInput), daemon=True)
    setupThread.start()
    httpServerSetup(everyLocalUrl,ipMonitor,fps)
    Gtk.main()

def stop():
    Gtk.main_quit()
    #Join all the threads
    fb.stop()
    print("Exiting")

if __name__ == "__main__":
    main()
    