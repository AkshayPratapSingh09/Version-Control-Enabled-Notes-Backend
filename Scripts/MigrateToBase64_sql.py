# scripts/migrate_to_base64_sql.py
import os
from sqlalchemy.orm import Session
from databases.sql_connect import SessionLocal, engine
from models.sql_models import Note, NoteHistory
from utils_b64 import b64e, is_b64

def migrate():
    with SessionLocal() as db:
        notes = db.query(Note).all()
        changed = 0
        for n in notes:
            upd = False
            if n.note_title and not is_b64(n.note_title):
                n.note_title = b64e(n.note_title); upd = True
            if n.note_description and not is_b64(n.note_description):
                n.note_description = b64e(n.note_description); upd = True
            if upd:
                changed += 1
        db.commit()
    print(f"Migrated {changed} notes to Base64.")

if __name__ == "__main__":
    migrate()
