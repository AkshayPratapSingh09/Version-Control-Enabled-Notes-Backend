
import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import List

from auth import JWT_SECRET, JWT_ALGO, ACCESS_TOKEN_EXPIRE_MINUTES, Token, get_current_email
from utils import hash_password, verify_password, create_access_token

from models.auth_models import RegisterIn, LoginIn, UserOut
from models.notes import NoteCreate, NoteUpdate, NoteOut

DB_BACKEND = os.getenv("DB_BACKEND", "mongo").lower()
app = FastAPI(title=f"FastAPI Notes Secure ({DB_BACKEND.upper()})", version="1.0.0")

# ---------- AUTH ----------
if DB_BACKEND == "sql":
    from databases.sql_connect import SessionLocal, engine, Base
    from models.sql_models import User, Note, NoteHistory
    from repositories.sql_users_repository import find_user_by_email as sql_find_user, create_user as sql_create_user
    from repositories.sql_notes_repository import add_note as sql_add, get_all_notes as sql_all
    Base.metadata.create_all(bind=engine)

    def get_sql_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    @app.post("/auth/register", response_model=UserOut, status_code=201)
    def register(payload: RegisterIn, db=Depends(get_sql_db)):
        if sql_find_user(db, payload.email):
            raise HTTPException(status_code=409, detail="Email already registered")
        u = sql_create_user(db, payload.email, hash_password(payload.password))
        return UserOut(id=u.id, email=u.email)

    @app.post("/auth/login", response_model=Token)
    def login(form: OAuth2PasswordRequestForm = Depends(), db=Depends(get_sql_db)):
        u = sql_find_user(db, form.username)
        if not u or not verify_password(form.password, u.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        token = create_access_token({"sub": u.email}, JWT_SECRET, JWT_ALGO, ACCESS_TOKEN_EXPIRE_MINUTES)
        return Token(access_token=token)

    # ---------- NOTES (AUTH REQUIRED) ----------
    @app.post("/notes", response_model=NoteOut)
    def create_note(payload: NoteCreate, current_email: str = Depends(get_current_email), db=Depends(get_sql_db)):
        # ensure user exists (required for FK)
        u = sql_find_user(db, current_email)
        if not u:
            raise HTTPException(status_code=401, detail="User not found")
        created = sql_add(db, current_email, payload.note_title, payload.note_description)
        return NoteOut(**created)

    @app.get("/notes", response_model=List[NoteOut])
    def list_notes(current_email: str = Depends(get_current_email), db=Depends(get_sql_db)):
        return [NoteOut(**r) for r in sql_all(db, current_email)]

    @app.put("/notes/{unique_id}", response_model=NoteOut)
    def edit_note(unique_id: int, payload: NoteUpdate, current_email: str = Depends(get_current_email), db=Depends(get_sql_db)):
        # ownership validation
        n = db.query(Note).filter(Note.id == unique_id).first()
        if not n:
            raise HTTPException(status_code=404, detail="Note not found")
        owner = db.query(User).filter(User.email == current_email).first()
        if not owner or n.owner_id != owner.id:
            raise HTTPException(status_code=403, detail="Not allowed")

        # push current snapshot to history
        hist = NoteHistory(note_id=n.id, note_title=n.note_title, note_description=n.note_description)
        db.add(hist)
        # update live fields
        n.note_title = payload.note_title
        n.note_description = payload.note_description
        db.commit(); db.refresh(n)

        return NoteOut(
            uniqueID=n.id,
            note_title=n.note_title,
            note_description=n.note_description,
            note_created=n.note_created,
            owner_key=current_email,
            note_history=[],
        )

    @app.delete("/notes/{unique_id}", status_code=204)
    def delete_note(unique_id: int, current_email: str = Depends(get_current_email), db=Depends(get_sql_db)):
        n = db.query(Note).filter(Note.id == unique_id).first()
        if not n:
            raise HTTPException(status_code=404, detail="Note not found")
        owner = db.query(User).filter(User.email == current_email).first()
        if not owner or n.owner_id != owner.id:
            raise HTTPException(status_code=403, detail="Not allowed")
        db.delete(n); db.commit()
        return None

else:
    from databases.mongodb_connect import get_db
    from repositories.users_repository import find_user_by_email as mg_find_user, create_user as mg_create_user
    from repositories.notes_repository import add_note as mg_add, get_all_notes as mg_all
    from pymongo import ReturnDocument

    db = get_db()

    @app.post("/auth/register", response_model=UserOut, status_code=201)
    def register(payload: RegisterIn):
        if mg_find_user(payload.email):
            raise HTTPException(status_code=409, detail="Email already registered")
        u = mg_create_user(payload.email, hash_password(payload.password))
        return UserOut(email=u["email"])

    @app.post("/auth/login", response_model=Token)
    def login(form: OAuth2PasswordRequestForm = Depends()):
        u = mg_find_user(form.username)
        if not u or not verify_password(form.password, u["hashed_password"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        token = create_access_token({"sub": u["email"]}, JWT_SECRET, JWT_ALGO, ACCESS_TOKEN_EXPIRE_MINUTES)
        return Token(access_token=token)

    # ---------- NOTES (AUTH REQUIRED) ----------
    @app.post("/notes", response_model=NoteOut)
    def create_note(payload: NoteCreate, current_email: str = Depends(get_current_email)):
        if not mg_find_user(current_email):
            raise HTTPException(status_code=401, detail="User not found")
        created = mg_add(current_email, payload.note_title, payload.note_description)
        return NoteOut(**created)

    @app.get("/notes", response_model=List[NoteOut])
    def list_notes(current_email: str = Depends(get_current_email)):
        return [NoteOut(**r) for r in mg_all(current_email)]

    @app.put("/notes/{unique_id}", response_model=NoteOut)
    def edit_note(unique_id: int, payload: NoteUpdate, current_email: str = Depends(get_current_email)):
        notes = db["notes"]
        current = notes.find_one({"uniqueID": unique_id})
        if not current:
            raise HTTPException(status_code=404, detail="Note not found")
        if current.get("owner_key") != current_email:
            raise HTTPException(status_code=403, detail="Not allowed")

        prev_snapshot = {
            "note_title": current.get("note_title"),
            "note_description": current.get("note_description"),
            "archived_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc),
        }

        updated = notes.find_one_and_update(
            {"uniqueID": unique_id},
            {
                "$push": {"note_history": {"$each": [prev_snapshot], "$position": 0}},
                "$set": {"note_title": payload.note_title, "note_description": payload.note_description}
            },
            return_document=ReturnDocument.AFTER
        )
        updated.pop("_id", None)
        return NoteOut(**updated)

    @app.delete("/notes/{unique_id}", status_code=204)
    def delete_note(unique_id: int, current_email: str = Depends(get_current_email)):
        res = db["notes"].find_one({"uniqueID": unique_id})
        if not res:
            raise HTTPException(status_code=404, detail="Note not found")
        if res.get("owner_key") != current_email:
            raise HTTPException(status_code=403, detail="Not allowed")
        db["notes"].delete_one({"uniqueID": unique_id})
        return None
