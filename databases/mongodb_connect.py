
import os
from pymongo import MongoClient, ASCENDING

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "notes_db")
_client = None

def get_db():
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI)
        db = _client[DB_NAME]
        db["notes"].create_index([("uniqueID", ASCENDING)], unique=True)
        db["users"].create_index([("email", ASCENDING)], unique=True)
    return _client[DB_NAME]
