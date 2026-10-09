from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

response = client.get("/api/telemetry/latest")
print("GET response:", response.status_code, response.text)

data = {
    "temperatura": 25.0,
    "humedad": 50.0,
    "ph": 7.0,
    "tds": 200.0,
    "aguaAnalogico": 4095.0,
    "suelo": 1500.0
}
response = client.post("/api/telemetry/push", json=data)
print("POST response:", response.status_code, response.text)
