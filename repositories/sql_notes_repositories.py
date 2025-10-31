# repositories/sql_notes_repository.py
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from models.sql_models import Note, User
from utils import b64e, b64d

def add_note(db: Session, owner_email: str, note_title: str, note_description: str) -> Dict[str, Any]:
    owner = db.query(User).filter(User.email == owner_email).first()
    note = Note(
        note_title=b64e(note_title),
        note_description=b64e(note_description),
        owner_id=owner.id
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return {
        "uniqueID": note.id,
        "note_title": b64d(note.note_title),
        "note_description": b64d(note.note_description),
        "note_created": note.note_created,
        "owner_key": owner_email,
        "note_history": [],
    }

def get_all_notes(db: Session, owner_email: str) -> List[Dict[str, Any]]:
    owner = db.query(User).filter(User.email == owner_email).first()
    if not owner:
        return []
    notes = db.query(Note).filter(Note.owner_id == owner.id).order_by(Note.id.asc()).all()
    out: List[Dict[str, Any]] = []
    for n in notes:
        out.append({
            "uniqueID": n.id,
            "note_title": b64d(n.note_title),
            "note_description": b64d(n.note_description),
            "note_created": n.note_created,
            "owner_key": owner_email,
            "note_history": [],  # history optional; encode/decode similarly if used
        })
    return out
