from Vlib.Gst.PipeBlocks.RtspSrc import *
from Vlib.Gst.PipeBlocks.SaveOnFile import *
from Vlib.Gst.PipeBlocks.BufferGen import *
from Vlib.Gst.GstPipeRunner import *
from Vlib.Gst.PipeBlocks.AppSrc import *
import datetime
import time
import os
import sys
import threading
from gi.repository import Gst

class Recorder:
    def __init__(self, 
                 rtspSrcUrl, 
                 destinationFolder, 
                 fps, 
                 preTime,    # seconds to buffer before trigger
                 postTime,   # seconds to capture after trigger (optional)
                 fileName=None, 
                 cleanVideos=True,
                 ip='None'):
        # Initialize GStreamer (if not already done)
        Gst.init(None)
        self.rtspSrcUrl = rtspSrcUrl
        self.ip = ip
        self.destinationFolder = destinationFolder
        if not os.path.exists(destinationFolder):
            os.makedirs(destinationFolder)

        self.fps = fps
        self.preTime = preTime
        self.postTime = postTime
        self.fileName = fileName
        self.cleanVideos = cleanVideos

        # State flags
        self.buffering = False     # true when continuously buffering pre-recorded frames
        self.buffer = []           # will hold buffered frames (circular buffer)
        self.current_pts = 0       # for proper timestamping

        self.sinkPipe = None
        self.bufferGen = None
        self.caps = None

    def startBuffering(self):
        self._setupBufferStorage()
        # Set circular buffer size to hold exactly preTime seconds of frames.
        self.bufferGen.setBufferSize(self.preTime * self.fps)
        self.sinkPipe.startInThread()
        self.buffering = True
        print(f"[{self.ip}] Buffering started (pre-record duration = {self.preTime} sec)")

    def stopBuffering(self):
        if self.buffering:
            self.sinkPipe.stop()
            self.buffering = False
            # Get the buffered frames (if using "clean" mode, this will select I-frames, etc.)
            if self.cleanVideos:
                self.buffer = self.bufferGen.getBuffer()
            else:
                self.buffer = self.bufferGen.getDirtyBuffer()
            self.caps = self.bufferGen.getSampleCaps()
            if not self.buffer or len(self.buffer) == 0:
                print(f"[{self.ip}] No frames recorded during buffer time.")
            else:
                print(f"[{self.ip}] Buffered {len(self.buffer)} frames.")

    def capturePostEventFrames(self):
        print(f"[{self.ip}] Capturing post-event frames for {self.postTime} sec")
        # Create a temporary pipeline for capturing post-event frames
        rtspSrc = RtspSrc(self.rtspSrcUrl, RtspSrcMode.H265PARSE)
        postBufferGen = BufferGen(max_buffer_size=(self.postTime * self.fps))
        postSinkPipe = GstPipeRunner(rtspSrc.link(postBufferGen))
        postSinkPipe.startInThread()

        startTime = time.time()
        while (time.time() - startTime) < self.postTime:
            time.sleep(0.1)

        postSinkPipe.stop()
        # Retrieve the post-event frames
        if self.cleanVideos:
            postBuffer = postBufferGen.getBuffer()
        else:
            postBuffer = postBufferGen.getDirtyBuffer()
        print(f"[{self.ip}] Captured {len(postBuffer)} post-event frames")
        # Append the post-event frames to the pre-buffered frames
        self.buffer.extend(postBuffer)

    def save(self):
        if not self.buffer or len(self.buffer) == 0:
            print(f"[{self.ip}] No frames recorded; nothing to save.")
            return

        formattedDateTime = self._actualTime()
        self._setupSavePipe(formattedDateTime)
        self._runSavePipe()
        self._pushBuffer(self.buffer)
        self._stopSavePipe()
        print(f"[{self.ip}] Recording saved successfully.")

    def triggerRecording(self):
        """
        Stop buffering, (optionally) capture post-event frames, save the current buffer,
        and then resume buffering to capture new frames.
        """
        self.stopBuffering()
        if self.postTime > 0:
            self.capturePostEventFrames()
        self.save()
        self._resumeBufferStorage()

    def _setupBufferStorage(self):
        rtspSrc = RtspSrc(self.rtspSrcUrl, RtspSrcMode.H265PARSE)
        self.bufferGen = BufferGen(max_buffer_size=(self.preTime * self.fps))
        self.sinkPipe = GstPipeRunner(rtspSrc.link(self.bufferGen))

    def _setupSavePipe(self, formattedDateTime):
        self.srcSavePipe = AppSrc(caps=self.caps)
        if self.fileName is None:
            filename = f"{self.ip}_{formattedDateTime}.mp4"
        else:
            filename = self.fileName
        self.sinkSavePipe = SaveOnFile(folder_path=self.destinationFolder, fileName=filename)
        self.runnerSavePipe = GstPipeRunner(self.srcSavePipe.link(self.sinkSavePipe))

    def _runSavePipe(self):
        self.runnerSavePipe.startInThread()
        self.srcSavePipe.safeSetCaps(self.caps)

    def _pushBuffer(self, buffer):
        if not buffer:
            print("Buffer is empty")
            return

        for sample in buffer:
            if sample:
                gstBuffer = sample.get_buffer()

                # Assign sequential timestamps
                gstBuffer.pts = self._get_next_pts()
                gstBuffer.dts = gstBuffer.pts

                ret = self.srcSavePipe.emit(gstBuffer)
                if ret != Gst.FlowReturn.OK:
                    print(f"Error pushing buffer: {ret}")

    def _get_next_pts(self):
        frame_interval = int(1e9 / self.fps)  # nanoseconds per frame
        self.current_pts += frame_interval
        return self.current_pts

    def _stopSavePipe(self):
        self.srcSavePipe.EOS()

    def _actualTime(self):
        now = datetime.datetime.now()
        return now.strftime("%Y_%m_%d_%H_%M_%S")
    
    def _resumeBufferStorage(self):
        """
        Restart the RTSP pipeline to resume continuous buffering.
        """
        self.startBuffering()
        print(f"[{self.ip}] Buffering resumed.")

if __name__ == "__main__":
    # Example RTSP URL and destination folder for a single recorder test.
    rtsp_url = "rtsp://192.168.3.95:554/stream1"
    destination = "/home/item/Recordings"
    fps = 25
    preTime = 20   # Buffer 20 seconds before trigger
    postTime = 10  # Capture an additional 10 seconds after trigger

    # Create the recorder instance
    recorder = Recorder(rtsp_url, destination, fps, preTime, postTime, ip="192.168.3.95")
    
    # Start continuous buffering (pre-recording)
    recorder.startBuffering()
    print("Buffering... waiting for trigger event")
    
    # Simulate waiting for an external trigger (e.g. motion detection)
    time.sleep(40)
    
    # Trigger recording: stops buffering, captures (optionally) post-event frames, saves the file,
    # and resumes buffering for new frames.
    recorder.triggerRecording()
    print("Recording finished!")
