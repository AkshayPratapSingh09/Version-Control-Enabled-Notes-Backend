
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from models.sql_models import Note, NoteHistory, User

def add_note(db: Session, owner_email: str, note_title: str, note_description: str) -> Dict[str, Any]:
    owner = db.query(User).filter(User.email == owner_email).first()
    note = Note(note_title=note_title, note_description=note_description, owner_id=owner.id)
    db.add(note)
    db.commit()
    db.refresh(note)
    return {
        "uniqueID": note.id,
        "note_title": note.note_title,
        "note_description": note.note_description,
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
            "note_title": n.note_title,
            "note_description": n.note_description,
            "note_created": n.note_created,
            "owner_key": owner_email,
            "note_history": [],
        })
    return out
