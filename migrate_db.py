from sqlalchemy import create_engine, text
from app.core.config import settings

url = settings.DATABASE_URL
if url.startswith("postgres://"):
    url = url.replace("postgres://", "postgresql+psycopg2://", 1)
elif url.startswith("postgresql://") and not url.startswith("postgresql+psycopg2://"):
    url = url.replace("postgresql://", "postgresql+psycopg2://", 1)

engine = create_engine(url)

with engine.begin() as conn:
    try:
        conn.execute(text("ALTER TABLE telemetry_logs RENAME COLUMN oxigeno TO suelo;"))
        print("Migracion completada: columna 'oxigeno' renombrada a 'suelo' exitosamente.")
    except Exception as e:
        print(f"Error durante la migracion: {e}")
