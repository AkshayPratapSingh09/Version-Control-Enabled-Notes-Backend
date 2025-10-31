# utils.py
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def utcnow():
    return datetime.now(timezone.utc)

def create_access_token(data: dict, secret: str, algo: str, minutes: int) -> str:
    payload = data.copy()
    expire = utcnow() + timedelta(minutes=minutes)
    payload.update({"exp": expire})
    return jwt.encode(payload, secret, algorithm=algo)
