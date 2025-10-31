from fastapi import FastAPI, HTTPException
from typing import List

from databases.mongodb_connect import get_db
from models.notes import NoteCreate, NoteUpdate, NoteOut
from repositories.notes_repository import add_note, get_all_notes, update_note, delete_note

app = FastAPI(title="Notes API", version="0.2.0")
db = get_db()

@app.post("/notes", response_model=NoteOut)
def create_note(payload: NoteCreate):
    created = add_note(db, payload.note_title, payload.note_description)
    return NoteOut(**created)

@app.get("/notes", response_model=List[NoteOut])
def list_notes():
    records = get_all_notes(db)
    return [NoteOut(**r) for r in records]

@app.put("/notes/{unique_id}", response_model=NoteOut)
def edit_note(unique_id: int, payload: NoteUpdate):
    updated = update_note(db, unique_id, payload.note_title, payload.note_description)
    if not updated:
        raise HTTPException(status_code=404, detail="Note not found")
    return NoteOut(**updated)

@app.delete("/notes/{unique_id}", status_code=204)
def remove_note(unique_id: int):
    ok = delete_note(db, unique_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Note not found")
    return None
