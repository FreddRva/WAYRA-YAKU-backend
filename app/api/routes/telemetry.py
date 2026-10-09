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

@router.get("/api/telemetry/latest")
def get_latest_telemetry(db: Session = Depends(get_db)):
    record = db.query(TelemetryRecord).order_by(TelemetryRecord.timestamp.desc()).first()
    if not record:
        return {}
    return {
        "timestamp": record.timestamp.isoformat() if record.timestamp else None,
        "temperatura": record.temperatura,
        "humedad": record.humedad,
        "ph": record.ph,
        "tds": record.tds,
        "turbidez": record.turbidez,
        "aguaAnalogico": record.aguaAnalogico,
        "caudal": record.caudal,
        "oxigeno": record.oxigeno,
        "presion": record.presion,
        "aire": record.aire,
        "sedimento": record.sedimento,
        "temp_liquido": record.temp_liquido,
        "is_anomaly": record.is_anomaly,
        "anomaly_score": record.anomaly_score,
        "status": record.status_label,
        "anomalous_sensors": record.anomalous_sensors.split(",") if record.anomalous_sensors else []
    }
