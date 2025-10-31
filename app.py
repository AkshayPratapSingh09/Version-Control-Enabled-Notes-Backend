# app.py
from fastapi import FastAPI, HTTPException
from typing import List

from databases.mongodb_connect import get_db
from models.notes import NoteCreate, NoteOut
from repositories.notes_repository import add_note, get_all_notes

app = FastAPI(title="Notes API", version="0.1.0")

db = get_db()

@app.post("/notes", response_model=NoteOut)
def create_note(payload: NoteCreate):
    created = add_note(db, payload.note_title, payload.note_description)
    return NoteOut(**created)

@app.get("/notes", response_model=List[NoteOut])
def list_notes():
    records = get_all_notes(db)
    return [NoteOut(**r) for r in records]
