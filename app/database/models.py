from sqlalchemy import Column, Integer, Float, Boolean, String, DateTime, func
from app.database.session import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String, default="trabajador")
    reset_token = Column(String, nullable=True)

class TelemetryRecord(Base):
    __tablename__ = "telemetry_logs"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Sensores
    temperatura = Column(Float, default=0.0)
    humedad = Column(Float, default=0.0)
    ph = Column(Float, default=0.0)
    tds = Column(Float, default=0.0)
    turbidez = Column(Float, default=0.0)
    aguaAnalogico = Column(Float, default=0.0)
    caudal = Column(Float, default=0.0)
    suelo = Column("oxigeno", Float, default=0.0)
    presion = Column(Float, default=0.0)
    aire = Column(Float, default=0.0)
    sedimento = Column(Float, default=0.0)
    temp_liquido = Column(Float, default=0.0)
    
    # IA
    is_anomaly = Column(Boolean, default=False)
    anomaly_score = Column(Float, default=0.0)
    status_label = Column(String, default="normal")
    anomalous_sensors = Column(String, default="")
