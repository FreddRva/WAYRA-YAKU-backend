from app.database.session import SessionLocal
from app.database.models import TelemetryRecord
import traceback

db = SessionLocal()
try:
    count = db.query(TelemetryRecord).count()
    print("Record count:", count)
    if count > 0:
        record = db.query(TelemetryRecord).order_by(TelemetryRecord.timestamp.desc()).first()
        print("Latest record dict:", record.__dict__)
except Exception as e:
    print("DB error:")
    traceback.print_exc()
