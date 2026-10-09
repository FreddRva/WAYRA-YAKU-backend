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
    # 1. Obtener el último registro para heredar los valores de los otros ESP32
    last_record = db.query(TelemetryRecord).order_by(TelemetryRecord.timestamp.desc()).first()
    
    # 2. Obtener SOLO los datos que este ESP32 específico envió en su JSON
    provided_data = data.model_dump(exclude_unset=True)
    
    # 3. Mezclar los datos: Tomamos lo último conocido y lo pisamos con lo nuevo
    merged_data = {
        "temperatura": getattr(last_record, 'temperatura', 0.0) if last_record else 0.0,
        "humedad": getattr(last_record, 'humedad', 0.0) if last_record else 0.0,
        "ph": getattr(last_record, 'ph', 0.0) if last_record else 0.0,
        "tds": getattr(last_record, 'tds', 0.0) if last_record else 0.0,
        "turbidez": getattr(last_record, 'turbidez', 0.0) if last_record else 0.0,
        "aguaAnalogico": getattr(last_record, 'aguaAnalogico', 0.0) if last_record else 0.0,
        "caudal": getattr(last_record, 'caudal', 0.0) if last_record else 0.0,
        "oxigeno": getattr(last_record, 'oxigeno', 0.0) if last_record else 0.0,
        "presion": getattr(last_record, 'presion', 0.0) if last_record else 0.0,
        "aire": getattr(last_record, 'aire', 0.0) if last_record else 0.0,
        "sedimento": getattr(last_record, 'sedimento', 0.0) if last_record else 0.0,
        "temp_liquido": getattr(last_record, 'temp_liquido', 0.0) if last_record else 0.0,
    }
    
    merged_data.update(provided_data)

    if not ai_model.is_trained:
        ai_model.train("history.csv")
        
    resultado_ia = ai_model.predict_anomaly(merged_data)
    
    nuevo_registro = TelemetryRecord(
        **merged_data,
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
