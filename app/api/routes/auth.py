from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid

from app.database.session import get_db
from app.database.models import User
from app.schemas.user import RegisterSchema, LoginSchema, ForgotPasswordSchema, ResetPasswordSchema
from app.core.security import verify_password, get_password_hash, create_access_token

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register")
def register(user_data: RegisterSchema, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == user_data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Usuario ya existe")
        
    new_user = User(
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
        role=user_data.role
    )
    db.add(new_user)
    db.commit()
    return {"status": "success", "message": f"Usuario {user_data.username} registrado."}

@router.post("/login")
def login(login_data: LoginSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == login_data.username).first()
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
        
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer", "role": user.role, "username": user.username}

@router.post("/forgot-password")
def forgot_password(req: ForgotPasswordSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    reset_token = str(uuid.uuid4())
    user.reset_token = reset_token
    db.commit()
    return {"status": "success", "reset_token": reset_token}

@router.post("/reset-password")
def reset_password(req: ResetPasswordSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.reset_token == req.reset_token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Token inválido o expirado")
        
    user.password_hash = get_password_hash(req.new_password)
    user.reset_token = None
    db.commit()
    return {"status": "success", "message": "Contraseña actualizada."}
