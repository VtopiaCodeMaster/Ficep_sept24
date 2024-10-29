import requests
import time

def send_http_get(url, interval):
     
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("HTTP GET request sent successfully")
        else:
            print(f"Failed to send HTTP GET request. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while sending the HTTP GET request: {e} at time {time.time().strftime('%Y-%m-%d %H:%M:%S')}")
    

if __name__ == "__main__":
    url = "http://172.16.5.54:8080/recordings"
    interval = 60  # Replace X with the desired interval in seconds
    while True:
        send_http_get(url, interval)
        time.sleep(interval)