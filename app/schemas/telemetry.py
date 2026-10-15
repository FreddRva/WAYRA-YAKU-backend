from pydantic import BaseModel
from typing import Optional

class TelemetryData(BaseModel):
    temperatura: Optional[float] = None
    humedad: Optional[float] = None
    ph: Optional[float] = None
    tds: Optional[float] = None
    turbidez: Optional[float] = None
    aguaAnalogico: Optional[float] = None
    caudal: Optional[float] = None
    suelo: Optional[float] = None
    presion: Optional[float] = None
    aire: Optional[float] = None
    sedimento: Optional[float] = None
    temp_liquido: Optional[float] = None

