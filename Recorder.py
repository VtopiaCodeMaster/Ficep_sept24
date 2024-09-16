import os
import gi
import datetime
import time
import sys
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject, GLib

class Recorder:
    def __init__(self,ip):
        Gst.init(None)
        self.ip = ip
        self.buffer_duration = 30
        self.fps = 18       # frames per second
        self.max_buffer_size = self.fps * self.buffer_duration # Total frames to store
        self.buffer = []
        self.request_recording = False
        self.record_saved = False
        self.folder_path = '/home/item/RecordingsFicep'
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)
            print(f"Folder '{self.folder_path}' created")


    
    def _on_new_sample(self, sink):
        sample = sink.emit('pull-sample')
        if sample:
            #with self.buffer_lock:
            self.buffer.append(sample)
            #print(f"Sample received. Buffer size: {len(self.buffer)}")  # Log buffer size
            # Remove old samples to maintain the buffer duration
            while len(self.buffer) > self.max_buffer_size:
                old_sample = self.buffer.pop(0)
                    
        return Gst.FlowReturn.OK

    def _on_message(self, bus, message):
        if message.type == Gst.MessageType.EOS:
            print("End-of-stream reached.")
            if self.request_recording and not self.record_saved:
                self.on_request()
        elif message.type == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print(f"Error: {err}: {debug}")
            self.loop.quit()
    
    def setup_pipeline(self):
        pipe_str = (
        f"rtspsrc location=rtsp://192.168.3.{self.ip}:554/stream1 latency=100 ! queue max-size-bytes=294967295 ! "
        f"rtph265depay ! h265parse ! queue ! appsink name=app_sink{self.ip} emit-signals=true sync=false"
        )
    
        self.pipeline = Gst.parse_launch(pipe_str)
        self.sink = self.pipeline.get_by_name(f'app_sink{self.ip}')
        self.sink.connect('new-sample', self._on_new_sample)

        
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect('message', self._on_message)
        
    def start_pipeline(self):
        self.pipeline.set_state(Gst.State.PLAYING)
        try:
            self.loop = GLib.MainLoop()
            self.loop.run()
        except Exception as e:
            print(e)
            self.pipeline.set_state(Gst.State.NULL)
            self.loop.quit()

    def on_request(self):
        self.pipeline.set_state(Gst.State.PAUSED)
        print("Recording paused.")
        now = datetime.datetime.now()
        formatted_date_time = now.strftime("%Y_%m_%d_%H_%M_%S")
        self.pipeline_save = Gst.parse_launch(
            "appsrc name=app_src is-live=true ! "
            "h265parse ! qtmux ! video/quicktime ! "
            f"filesink location={self.folder_path}/Rec{self.ip}_{formatted_date_time}.mp4"
        )
        app_src = self.pipeline_save.get_by_name('app_src')
        if self.buffer:
            # Get caps from the first sample and set it on appsrc
            sample_caps = self.buffer[0].get_caps()
            app_src.set_property('caps', sample_caps)
        else:
            print("Buffer is empty.")
            return
        self.pipeline_save.set_state(Gst.State.PLAYING)
        for sample in self.buffer:
            if sample:
                buffer_data = sample.get_buffer()
                ret = app_src.emit('push-buffer', buffer_data)
                if ret != Gst.FlowReturn.OK:
                    print(f"Error pushing buffer: {ret}")
        print("Recording saved.")
        self.record_saved = True
        # Signal end-of-stream (EOS) after all buffers are pushed
        app_src.emit('end-of-stream')
        time.sleep(5)
        self.pipeline.set_state(Gst.State.PLAYING)
        self.pipeline_save.set_state(Gst.State.NULL)
    
    def cleanupFolder(self):
        folder_path = '/home/item/RecordingsFicep'
        if not os.path.exists(folder_path):
            print("Folder not found.")
            return
        for file in os.listdir(folder_path):
            if file.endswith('.mp4'):
                os.remove(os.path.join(folder_path, file))
        print("Folder cleaned.")
    
    def stop_pipeline(self):
        self.pipeline.set_state(Gst.State.NULL)
        self.loop.quit()
        print("Pipeline stopped.")
        sys.exit(0)

