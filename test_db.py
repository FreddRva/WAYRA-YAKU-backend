from app.database.session import SessionLocal
from app.database.models import User
import sys
import traceback

try:
    db = SessionLocal()
    # Test query
    users = db.query(User).all()
    print("Success. Users:", users)
    
    # Try creating one
    from app.core.security import get_password_hash
    new_user = User(username="test_script", password_hash=get_password_hash("test1234"), role="supervisor")
    db.add(new_user)
    db.commit()
    print("User created!")
    
except Exception as e:
    print("ERROR OCCURRED:")
    traceback.print_exc()
