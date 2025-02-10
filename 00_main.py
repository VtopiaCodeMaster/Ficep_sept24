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


def setupOutput(fps,localInput):
    outputs = {}
    for ipLoc in localInput:
        output = FBOutput(type = FBOutputType.streamSelector,
                            name=f"output{ipLoc}",
                            src = [ipLoc],
                            fps = int(fps))
        outputs[f"output{ipLoc}"] = output
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
        lsb=LiveStreamBuffer(name=f"lsb{output}", bufferSize=10)
        pipe = GstPipeRunner(appsrc.link(Resize(960,540)).link(lsb).link(sink))
        DA = GstDrawingArea(nvGleSink=sink, defaultSize=(960, 540), defaultPosition=position.pop(0))
        GLib.idle_add(win.addGstDrawingArea, DA)
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
    GLib.idle_add(win.show_all)

def setupRecording(localUrls: Dict[str, str]):
    listUrls = list(localUrls.values())
    recorder=SetupRecording(urls=listUrls,destinationFolder="/home/item/Recordings",ips=list(localUrls.keys()))
    return recorder

def httpServerSetup():
    recorder = setupRecording(everyLocalUrl)
    wrapped_callback = partial(saveBufferZip, recorder)
    httpServer = HttpGETServer(pathFileToBeDownloaded=['/home/item/Recordings.zip'],callback=[wrapped_callback],downloadRule=["/rec"],port=8080)
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
    
    
SNc = SNChecker(folderToClear="/home/item/Ficep_sept24",
              SNpath="/home/item/glibc-2.28/benchtests/strcoll-inputs/SN.txt")
SNc.check()

jsonDict = extract_local_dict("/home/item/Ficep_sept24/config.json")
everyLocalUrl = jsonDict["local"]
fps=jsonDict["fps"]
Gst.init(None)
fb = FrameBank()
localInput=setupLocalInput(everyLocalUrl)
outputs=setupOutput(fps,localInput)

win = Window("Basic Rtsp Pipe", defaultSize=(1920, 1080), defaultPosition=(0, 0))
win.start()
setupThread = Thread(target=startPipes, args=(win,), daemon=True)
setupThread.start()
httpServerSetup()
Gtk.main()
