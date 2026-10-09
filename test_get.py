import requests
url = "https://wayra-yaku-backend.onrender.com/api/telemetry/latest"
try:
    response = requests.get(url)
    print(response.status_code)
    print(response.text)
except Exception as e:
    print(e)
