from pydantic import BaseModel

class RegisterSchema(BaseModel):
    username: str
    password: str
    role: str = "trabajador"

class LoginSchema(BaseModel):
    username: str
    password: str

class ForgotPasswordSchema(BaseModel):
    username: str

class ResetPasswordSchema(BaseModel):
    reset_token: str
    new_password: str
