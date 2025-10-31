from typing import Dict, Any, List
from sqlalchemy.orm import Session
from models.sql_models import Note, NoteHistory

def add_note(db: Session, note_title: str, note_description: str) -> Dict[str, Any]:
    note = Note(note_title=note_title, note_description=note_description)
    db.add(note)
    db.commit()
    db.refresh(note)
    return {
        "uniqueID": note.id,
        "note_title": note.note_title,
        "note_description": note.note_description,
        "note_created": note.note_created,
        "note_history": [],  # snapshots only added during edits (not in this minimal 2-func repo)
    }

def get_all_notes(db: Session) -> List[Dict[str, Any]]:
    notes = db.query(Note).order_by(Note.id.asc()).all()
    out: List[Dict[str, Any]] = []
    for n in notes:
        snapshots = [
            {
                "note_title": h.note_title,
                "note_description": h.note_description,
                "archived_at": h.archived_at,
            } for h in n.history
        ]
        out.append({
            "uniqueID": n.id,
            "note_title": n.note_title,
            "note_description": n.note_description,
            "note_created": n.note_created,
            "note_history": snapshots,
        })
    return out
