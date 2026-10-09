import requests
url = "https://wayra-yaku-backend.onrender.com/api/telemetry/push"
data = {
    "temperatura": 25.0,
    "humedad": 50.0,
    "ph": 7.0,
    "tds": 200.0,
    "aguaAnalogico": 4095.0,
    "suelo": 1500.0
}
try:
    response = requests.post(url, json=data)
    print("Push status:", response.status_code)
    print("Push response:", response.text)
except Exception as e:
    print(e)
