import os
import shutil
import tempfile
import threading
import time
from flask import Flask, send_file, jsonify
from Recorder import Recorder
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
recorders = []  # To hold the Recorder objects
recorders_lock = threading.Lock()  # For thread-safe access to recorders

every_ip = [50,51,52,53]  # List of IPs

# Function to set up the recorder for each IP
def rec_setup(ip,url):
    rec = Recorder(ip,url)
    rec.setup_pipeline()
    threading.Thread(target=rec.start_pipeline).start()

    with recorders_lock:
        recorders.append(rec)  # Store the Recorder object safely
    logging.info(f"Recorder for IP {ip} set up and pipeline started.")

# Function to start recording pipelines in separate threads
def start_recorders(every_ip,everyUrl):
    for ip in every_ip:
        threading.Thread(target=rec_setup, args=(ip,everyUrl[ip])).start()

# Function to trigger on_request() for each recorder concurrently
def trigger_on_requests():
    threads = []
    
    # Trigger on_request in a separate thread for each recorder
    with recorders_lock:
        for rec in recorders:
            thread = threading.Thread(target=rec.on_request)
            threads.append(thread)
            thread.start()
    
    # Wait for all on_request calls to complete
    for thread in threads:
        thread.join()

@app.route('/recordings', methods=['GET'])
def download_recordings():
    # Trigger the on_request for each recorder concurrently
    trigger_on_requests()
    
    # Wait for a short period to allow recordings to be captured (adejust time if needed)
    time.sleep(5)

    # Specify the folder to be downloaded
    folder_path = '/home/item/RecordingsFicep'
    logging.info(f"Folder path: {folder_path}")

    # Ensure the folder exists
    if not os.path.exists(folder_path):
        logging.error(f"Folder '{folder_path}' not found.")
        return jsonify({"error": "Folder not found"}), 404

    try:
        # Create a temporary directory for the zip file
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, 'recordings.zip')

        # Create a zip file of the folder
        shutil.make_archive(zip_path.replace('.zip', ''), 'zip', folder_path)
        logging.info("Zip file created")

        # Send the zip file as a response
        response = send_file(zip_path, as_attachment=True)
        logging.info("Response sent successfully")

        # Clean up the temporary directory after the request is finished
        shutil.rmtree(temp_dir)
        logging.info("Temporary directory cleaned")

        # Call cleanupFolder() on each recorder after sending the response
        with recorders_lock:
            for rec in recorders:
                rec.cleanupFolder()
        logging.info("Recorder folders cleaned up")

        return response

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return jsonify({"error": "Failed to process request"}), 500

def HttpPoller(every_ip,everyUrl):
    # Start the recorders
    start_recorders(every_ip,everyUrl)
    # Run the Flask app
    app.run(host='0.0.0.0', port=8000)
