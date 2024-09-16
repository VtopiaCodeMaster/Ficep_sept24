import gi
gi.require_version("Gst", "1.0")
gi.require_version("GstRtsp", "1.0")
from gi.repository import Gst, GLib
import time
import threading
import os
from datetime import datetime
import os
import re
from moviepy.editor import VideoFileClip, concatenate_videoclips

def clean_up_folder(folder_path, prefix, keep_last_n):
    # Create a pattern to match files with the specified prefix and a four-digit id
    pattern = re.compile(f"^{re.escape(prefix)}(\\d{{4}})\\.mp4$")
    
    # List all files in the directory and filter them based on the pattern
    files = [f for f in os.listdir(folder_path) if pattern.match(f)]
    
    # Sort files by the numeric part of the filename
    files.sort(key=lambda x: int(pattern.match(x).group(1)))
    
    # Determine the files to delete (all but the last N)
    if keep_last_n > 0:
        files_to_delete = files[:-keep_last_n] if len(files) > keep_last_n else []
    else:
        files_to_delete = files
    # Delete the files determined to be removed
    for file in files_to_delete:
        os.remove(os.path.join(folder_path, file))
        print(f"Deleted: {file}")

    # Optional: List remaining files
    remaining_files = files[-keep_last_n:]
    print("Remaining files:")
    for file in remaining_files:
        print(file)


def merge_videos(folder_path, prefix, output_filename):

    # Create a pattern to match files with the specified prefix and a numeric sequence
    pattern = re.compile(f"^{re.escape(prefix)}(\\d+)\\.mp4$")
    
    # List all matching .mp4 files in the directory
    files = [f for f in os.listdir(folder_path) if pattern.match(f)]
    
    # Sort files by numeric order extracted from the filename
    files.sort(key=lambda x: int(pattern.match(x).group(1)))
    
    # Load all video files into moviepy VideoFileClip objects
    clips = [VideoFileClip(os.path.join(folder_path, f)) for f in files]
    
    # Concatenate all video clips into one video clip
    final_clip = concatenate_videoclips(clips, method="compose")
    
    # Write the concatenated video to disk
    final_clip.write_videofile(os.path.join(folder_path, output_filename), codec="libx264")
    
    # Close all clips to free up resources
    for clip in clips:
        clip.close()

class Recorder:
    def __init__(self,cam_ip,rec_time=5):
        self.cam_ip = cam_ip
        self.rec_time = rec_time
        self.url=f"rtsp://192.168.3.{self.cam_ip}:554/stream1"
        self.createPipeline()
        self.stop=False


    def fname(self):
        now=datetime.now()
        data= now.strftime("%Y_%m_%d")
        ora=now.strftime("%H_%M_%S")
        return f"cam_{self.cam_ip}_{data}_{ora}.mp4"

    def createPipeline(self):
        self.pipeline = Gst.parse_launch(
                f"rtspsrc udp-buffer-size=212000 location={self.url} name=src ! "
                f"rtph265depay ! h265parse config-interval=-1 ! "
                f"queue name=q0 ! " 
                f"splitmuxsink location=/home/item/Recordings/tmp{self.cam_ip}_%04d.mp4 max-size-time={self.rec_time*100000000}"
            )
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect("message", self.on_message)
            
        return self.pipeline
    
    def start(self):
        self.pipeline.set_state(Gst.State.PLAYING)
        threading.Timer(self.rec_time, self.delete_old_files).start()

    def on_message(self, bus, message):
        t = message.type
        if t == Gst.MessageType.EOS:
            print("End-of-stream")
            self.pipeline.set_state(Gst.State.NULL)
            self.createPipeline()
            self.start()
        elif t == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print(f"Error: {err}, debug: {debug}")
            self.pipeline.set_state(Gst.State.NULL)
            self.createPipeline()
            self.start()
        elif t == Gst.MessageType.WARNING:
            err, debug = message.parse_warning()
            print(f"Warning: {err}, debug: {debug}")
        else:
            print(f"Message: {t}")
    
    def record(self):
        if self.pipeline is None:
            return
        self.stop=True
        self.pipeline.send_event(Gst.Event.new_eos())
        time.sleep(2)
        self.pipeline.set_state(Gst.State.NULL)
        time.sleep(2)
        clean_up_folder("/home/item/Recordings", f"tmp{self.cam_ip}_", 5)
        merge_videos("/home/item/Recordings", f"tmp{self.cam_ip}_", self.fname())
        clean_up_folder("/home/item/Recordings", f"tmp{self.cam_ip}_", 0)    

        

    def delete_old_files(self):
        clean_up_folder("/home/item/Recordings", f"tmp{self.cam_ip}_", 5)
        if not self.stop:
            threading.Timer(self.rec_time, self.delete_old_files).start()
        pass





def recordingAll(ips=[80,85,95,115]):
    cam_recording = {}
    for ip in ips:
        cam_recording[ip] = Recorder(ip)
        threading.Thread(cam_recording[ip].start(), daemon=True).start()
    print(f"Recorder {ips} started")
    #time.sleep(18)
    print(f"saving {ips} now!")
    for ip in ips:
        cam_recording[ip].record()


Gst.init(None)
recordingAll()

#TODO:
# - fix record timings: idk why, but setting '1' does not correspond to 1 second
# - implement in the main