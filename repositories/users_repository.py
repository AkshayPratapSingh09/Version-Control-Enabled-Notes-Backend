
from typing import Optional
from databases.mongodb_connect import get_db

def users_col():
    return get_db()["users"]

def find_user_by_email(email: str) -> Optional[dict]:
    return users_col().find_one({"email": email})

def create_user(email: str, hashed_password: str) -> dict:
    doc = {"email": email, "hashed_password": hashed_password}
    users_col().insert_one(doc)
    doc.pop("_id", None)
    return doc
