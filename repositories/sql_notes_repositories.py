from typing import Dict, Any, List
from sqlalchemy.orm import Session
from models.sql_models import Note, User, NoteMedia as SQLNoteMedia
from utils_b64 import b64e, b64d

def add_note(db: Session, owner_email: str, note_title: str, note_description: str, media: List[Dict[str, Any]] | None = None) -> Dict[str, Any]:
    owner = db.query(User).filter(User.email == owner_email).first()
    note = Note(
        note_title=b64e(note_title),
        note_description=b64e(note_description),
        owner_id=owner.id
    )
    db.add(note); db.flush()
    for m in (media or []):
        db.add(SQLNoteMedia(
            note_id=note.id,
            url=m["url"],
            mime_type=m["mime_type"],
            size_bytes=m["size_bytes"],
            original_name=m["original_name"],
        ))
    db.commit(); db.refresh(note)

    out_media = [
        {"url": m.url, "mime_type": m.mime_type, "size_bytes": m.size_bytes, "original_name": m.original_name}
        for m in db.query(SQLNoteMedia).filter(SQLNoteMedia.note_id == note.id).all()
    ]

    return {
        "uniqueID": note.id,
        "note_title": b64d(note.note_title),
        "note_description": b64d(note.note_description),
        "note_created": note.note_created,
        "owner_key": owner_email,
        "note_history": [],
        "media": out_media,
    }

def get_all_notes(db: Session, owner_email: str) -> List[Dict[str, Any]]:
    owner = db.query(User).filter(User.email == owner_email).first()
    if not owner:
        return []
    notes = db.query(Note).filter(Note.owner_id == owner.id).order_by(Note.id.asc()).all()
    out: List[Dict[str, Any]] = []
    for n in notes:
        medias = db.query(SQLNoteMedia).filter(SQLNoteMedia.note_id == n.id).all()
        out.append({
            "uniqueID": n.id,
            "note_title": b64d(n.note_title),
            "note_description": b64d(n.note_description),
            "note_created": n.note_created,
            "owner_key": owner_email,
            "note_history": [],
            "media": [{"url": m.url, "mime_type": m.mime_type, "size_bytes": m.size_bytes, "original_name": m.original_name} for m in medias],
        })
    return out
