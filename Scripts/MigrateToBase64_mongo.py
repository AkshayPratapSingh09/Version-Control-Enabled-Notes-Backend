import os
from pymongo import MongoClient
from utils_b64 import b64e, is_b64

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "notes_db")

def migrate():
    cli = MongoClient(MONGO_URI)
    col = cli[DB_NAME]["notes"]
    count = 0
    for doc in col.find({}):
        needs_update = False
        title = doc.get("note_title")
        desc = doc.get("note_description")

        if title is not None and not is_b64(title):
            title = b64e(title); needs_update = True
        if desc is not None and not is_b64(desc):
            desc = b64e(desc); needs_update = True

        hist = doc.get("note_history", [])
        new_hist = []
        hist_changed = False
        for h in hist:
            t = h.get("note_title", "")
            d = h.get("note_description", "")
            ch = False
            if t and not is_b64(t): t = b64e(t); ch = True
            if d and not is_b64(d): d = b64e(d); ch = True
            if ch: hist_changed = True
            new_hist.append({"note_title": t, "note_description": d, "archived_at": h.get("archived_at")})

        if hist_changed: needs_update = True

        if needs_update:
            col.update_one({"_id": doc["_id"]}, {"$set": {
                "note_title": title,
                "note_description": desc,
                "note_history": new_hist
            }})
            count += 1
    print(f"Migrated {count} documents to Base64.")

if __name__ == "__main__":
    migrate()
