from typing import Optional
from sqlalchemy.orm import Session
from models.sql_models import User

def find_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, email: str, hashed_password: str) -> User:
    u = User(email=email, hashed_password=hashed_password)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u
