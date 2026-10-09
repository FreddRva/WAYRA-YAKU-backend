from pydantic import BaseModel

class TelemetryData(BaseModel):
    temperatura: float = 0.0
    humedad: float = 0.0
    ph: float = 0.0
    tds: float = 0.0
    turbidez: float = 0.0
    aguaAnalogico: float = 0.0
    caudal: float = 0.0
    suelo: float = 0.0
    presion: float = 0.0
    aire: float = 0.0
    sedimento: float = 0.0
    temp_liquido: float = 0.0
