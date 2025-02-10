from Rec import Recorder
import time
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0')
from gi.repository import Gst, GLib
import threading

class SetupRecording():
    def __init__(self, urls, destinationFolder,ips):
        self.recorders = []
        fps = 25
        self.destinationFolder = destinationFolder
        preTime = 20    # seconds to buffer before trigger
        postTime = 0    # seconds to capture after trigger (set to 0 if not used)
        
        # Create a Recorder instance for each URL.
        for url,i in zip(urls, ips):
            rec = Recorder(
                rtspSrcUrl = url,
                destinationFolder = self.destinationFolder,
                fps = fps,
                preTime = preTime,
                postTime=postTime,  # total duration (pre + post)
                fileName = None,
                cleanVideos = True,
                ip = i
            )
            self.recorders.append(rec)
        
        for rec in self.recorders:
            rec.startBuffering()

    def _trigger_wrapper(self, rec, barrier):
        barrier.wait()      
        rec.triggerRecording()  

    def saveBuffer(self):
        num = len(self.recorders)
        trigger_barrier = threading.Barrier(num)
        threads = []
        for rec in self.recorders:
            t = threading.Thread(target=self._trigger_wrapper, args=(rec, trigger_barrier))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        print("Buffers saved for all recorders.")

    def getDestinationFolder(self):
        return self.destinationFolder


if __name__ == "__main__":
    urls = [
        "rtsp://192.168.3.95:554/stream1",
        "rtsp://192.168.3.85:554/stream1",
        "rtsp://192.168.3.80:554/stream1",
        "rtsp://192.168.3.105:554/stream1"
    ]
    destinationFolder = "/home/item/Recordings"
    
    # Create the RecorderPre instance (one per camera)
    recorderPre = SetupRecording(urls, destinationFolder)
    
    print("Buffering... waiting for the pre-record buffer to fill.")
    time.sleep(40)  # Wait for the pre-record buffers to fill.
    
    # When you want to save the current buffer, simply call:
    recorderPre.saveBuffer()
    
    print("Recording done")
