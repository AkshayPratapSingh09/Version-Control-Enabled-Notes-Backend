import os
from fastapi import FastAPI, Depends, HTTPException
from typing import List
from models.notes import NoteCreate, NoteOut

DB_BACKEND = os.getenv("DB_BACKEND", "mongo").lower()
app = FastAPI(title=f"FastAPI Notes ({DB_BACKEND.upper()})", version="0.3.0")

if DB_BACKEND == "sql":
    # SQL wiring
    from databases.sql_connect import SessionLocal, engine, Base
    from repositories.sql_notes_repository import add_note as sql_add, get_all_notes as sql_all

    Base.metadata.create_all(bind=engine)
    def get_sql_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    @app.post("/notes", response_model=NoteOut)
    def create_note(payload: NoteCreate, db=Depends(get_sql_db)):
        return NoteOut(**sql_add(db, payload.note_title, payload.note_description))

    @app.get("/notes", response_model=List[NoteOut])
    def list_notes(db=Depends(get_sql_db)):
        return [NoteOut(**r) for r in sql_all(db)]

else:
    # Mongo wiring (existing)
    from databases.mongodb_connect import get_db
    from repositories.notes_repository import add_note as mg_add, get_all_notes as mg_all
    db = get_db()

    @app.post("/notes", response_model=NoteOut)
    def create_note(payload: NoteCreate):
        return NoteOut(**mg_add(db, payload.note_title, payload.note_description))

    @app.get("/notes", response_model=List[NoteOut])
    def list_notes():
        return [NoteOut(**r) for r in mg_all(db)]
