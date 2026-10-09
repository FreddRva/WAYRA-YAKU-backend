from app.database.session import SessionLocal
from app.database.models import User
from app.core.security import get_password_hash
import sys

try:
    db = SessionLocal()
    
    # 1. Supervisor
    sup = db.query(User).filter(User.username == "supervisor").first()
    if not sup:
        sup = User(username="supervisor", password_hash=get_password_hash("admin123"), role="supervisor")
        db.add(sup)
        print("Supervisor created")
    
    # 2. Mantenimiento
    mant = db.query(User).filter(User.username == "mantenimiento").first()
    if not mant:
        mant = User(username="mantenimiento", password_hash=get_password_hash("mantenimiento123"), role="trabajador")
        db.add(mant)
        print("Mantenimiento created")
        
    db.commit()
    print("All users successfully inserted into Supabase!")
    
except Exception as e:
    print("ERROR OCCURRED:")
    import traceback
    traceback.print_exc()
