import requests
import datetime

BACKEND_URL = "http://127.0.0.1:5000/alert"

def send_alert(event_type, risk="HIGH", camera_id="CAM_01"):
    payload = {
        "event": event_type,
        "risk": risk,
        "camera_id": camera_id,
        "timestamp": str(datetime.datetime.now())
    }

    try:
        response = requests.post(BACKEND_URL, json=payload)
        print("📡 Alert sent:", response.status_code)
    except:
        print("❌ Backend not reachable")