from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth, telemetry
from app.services.ai_engine import ai_model

from app.database.session import engine, Base
from app.database.models import User, TelemetryRecord

# Crear tablas en la base de datos si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Telemetry AI Service Pro", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(telemetry.router)

@app.get("/")
def read_root():
    return {"status": "AI Service Running", "trained": ai_model.is_trained}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)
