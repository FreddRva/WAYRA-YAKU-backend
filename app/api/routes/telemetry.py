from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import TelemetryRecord
from app.schemas.telemetry import TelemetryData
from app.services.ai_engine import ai_model
import httpx

router = APIRouter(tags=["telemetry"])

@router.post("/api/telemetry/push")
def push_telemetry(data: TelemetryData, db: Session = Depends(get_db)):
    if not ai_model.is_trained:
        ai_model.train("history.csv")
        
    resultado_ia = ai_model.predict_anomaly(data.model_dump())
    
    nuevo_registro = TelemetryRecord(
        temperatura=data.temperatura,
        humedad=data.humedad,
        ph=data.ph,
        tds=data.tds,
        turbidez=data.turbidez,
        aguaAnalogico=data.aguaAnalogico,
        caudal=data.caudal,
        oxigeno=data.oxigeno,
        presion=data.presion,
        aire=data.aire,
        sedimento=data.sedimento,
        temp_liquido=data.temp_liquido,
        is_anomaly=resultado_ia["is_anomaly"],
        anomaly_score=resultado_ia["anomaly_score"],
        status_label=resultado_ia["status"],
        anomalous_sensors=",".join(resultado_ia["anomalous_sensors"])
    )
    
    try:
        db.add(nuevo_registro)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
    return {"status": "success", "ai_result": resultado_ia}

@router.get("/proxy/esp/{ip}")
async def proxy_esp(ip: str):
    # Ruta temporal por si se necesita leer directamente del ESP32 local
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"http://{ip}/sensor", timeout=2.0)
            return resp.json()
        except Exception:
            return None
