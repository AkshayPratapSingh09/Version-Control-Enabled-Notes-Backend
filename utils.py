# utils.py
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt
import base64

def b64e(txt: str) -> str:
    if txt is None:
        return ""
    return base64.b64encode(txt.encode("utf-8")).decode("ascii")

def b64d(txt: str) -> str:
    if not txt:
        return ""
    try:
        return base64.b64decode(txt.encode("ascii")).decode("utf-8")
    except Exception:
        return txt

def is_b64(txt: str) -> bool:
    if not txt:
        return False
    try:
        return b64e(b64d(txt)) == txt
    except Exception:
        return False


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
