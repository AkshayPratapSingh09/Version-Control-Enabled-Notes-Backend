import os
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from typing import List, Dict, Any
from datetime import datetime, timezone

from auth import JWT_SECRET, JWT_ALGO, ACCESS_TOKEN_EXPIRE_MINUTES, Token, get_current_email
from utils import hash_password, verify_password, create_access_token
from utils_b64 import b64e, b64d
from utils_media import save_upload, MAX_BYTES, ALLOWED_MIME

from models.auth_models import RegisterIn, UserOut
from models.notes import NoteCreate, NoteUpdate, NoteOut

DB_BACKEND = os.getenv("DB_BACKEND", "mongo").lower()
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")

app = FastAPI(title=f"FastAPI Notes Secure ({DB_BACKEND.upper()})", version="1.2.0")
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# ------------------ SQL BRANCH ------------------
if DB_BACKEND == "sql":
    from databases.sql_connect import SessionLocal, engine, Base
    from models.sql_models import User, Note, NoteHistory, NoteMedia as SQLNoteMedia
    from repositories.sql_users_repository import find_user_by_email as sql_find_user, create_user as sql_create_user
    from repositories.sql_notes_repository import add_note as sql_add, get_all_notes as sql_all

    Base.metadata.create_all(bind=engine)

    def get_sql_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    # --- Auth ---
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

    # --- Media upload (fault tolerant) ---
    @app.post("/media/upload")
    async def upload_media(files: List[UploadFile] = File(...), current_email: str = Depends(get_current_email)):
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        results: List[Dict[str, Any]] = []
        errors: List[Dict[str, str]] = []
        for f in files:
            meta, err = await save_upload(UPLOAD_DIR, f)
            if err:
                errors.append({"file": f.filename, "error": err})
                continue
            results.append(meta)
        return {"saved": results, "errors": errors, "limit_bytes": MAX_BYTES, "allowed": sorted(list(ALLOWED_MIME))}

    # --- Notes ---
    @app.post("/notes", response_model=NoteOut)
    def create_note(payload: NoteCreate, current_email: str = Depends(get_current_email), db=Depends(get_sql_db)):
        # ensure user exists
        u = sql_find_user(db, current_email)
        if not u:
            raise HTTPException(status_code=401, detail="User not found")
        created = sql_add(db, current_email, payload.note_title, payload.note_description, media=payload.media or [])
        return NoteOut(**created)

    @app.post("/notes/with-media", response_model=NoteOut)
    async def create_note_with_media(
        note_title: str = Form(...),
        note_description: str = Form(...),
        files: List[UploadFile] = File(default=[]),
        current_email: str = Depends(get_current_email),
        db=Depends(get_sql_db)
    ):
        u = sql_find_user(db, current_email)
        if not u:
            raise HTTPException(status_code=401, detail="User not found")
        saved_media = []
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        for f in files:
            meta, err = await save_upload(UPLOAD_DIR, f)
            if not err:
                saved_media.append(meta)
        created = sql_add(db, current_email, note_title, note_description, media=saved_media)
        return NoteOut(**created)

    @app.get("/notes", response_model=List[NoteOut])
    def list_notes(current_email: str = Depends(get_current_email), db=Depends(get_sql_db)):
        return [NoteOut(**r) for r in sql_all(db, current_email)]

    @app.put("/notes/{unique_id}", response_model=NoteOut)
    def edit_note(unique_id: int, payload: NoteUpdate, current_email: str = Depends(get_current_email), db=Depends(get_sql_db)):
        n = db.query(Note).filter(Note.id == unique_id).first()
        if not n:
            raise HTTPException(status_code=404, detail="Note not found")
        owner = sql_find_user(db, current_email)
        if not owner or n.owner_id != owner.id:
            raise HTTPException(status_code=403, detail="Not allowed")

        # push snapshot (Base64 in DB)
        hist = NoteHistory(note_id=n.id, note_title=n.note_title, note_description=n.note_description)
        db.add(hist)

        n.note_title = b64e(payload.note_title)
        n.note_description = b64e(payload.note_description)
        db.commit(); db.refresh(n)

        return NoteOut(
            uniqueID=n.id,
            note_title=b64d(n.note_title),
            note_description=b64d(n.note_description),
            note_created=n.note_created,
            owner_key=current_email,
            note_history=[],  # can be expanded to return decoded history if desired
            media=[{"url": m.url, "mime_type": m.mime_type, "size_bytes": m.size_bytes, "original_name": m.original_name}
                   for m in db.query(SQLNoteMedia).filter(SQLNoteMedia.note_id == n.id).all()]
        )

    @app.delete("/notes/{unique_id}", status_code=204)
    def delete_note(unique_id: int, current_email: str = Depends(get_current_email), db=Depends(get_sql_db)):
        n = db.query(Note).filter(Note.id == unique_id).first()
        if not n:
            raise HTTPException(status_code=404, detail="Note not found")
        owner = sql_find_user(db, current_email)
        if not owner or n.owner_id != owner.id:
            raise HTTPException(status_code=403, detail="Not allowed")
        db.delete(n); db.commit()
        return None

# ------------------ MONGO BRANCH ------------------
else:
    from databases.mongodb_connect import get_db
    from repositories.users_repository import find_user_by_email as mg_find_user, create_user as mg_create_user
    from repositories.notes_repository import add_note as mg_add, get_all_notes as mg_all
    from pymongo import ReturnDocument

    db = get_db()

    # --- Auth ---
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

    # --- Media upload (fault tolerant) ---
    @app.post("/media/upload")
    async def upload_media(files: List[UploadFile] = File(...), current_email: str = Depends(get_current_email)):
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        results: List[Dict[str, Any]] = []
        errors: List[Dict[str, str]] = []
        for f in files:
            meta, err = await save_upload(UPLOAD_DIR, f)
            if err:
                errors.append({"file": f.filename, "error": err})
                continue
            results.append(meta)
        return {"saved": results, "errors": errors, "limit_bytes": MAX_BYTES, "allowed": sorted(list(ALLOWED_MIME))}

    # --- Notes ---
    @app.post("/notes", response_model=NoteOut)
    def create_note(payload: NoteCreate, current_email: str = Depends(get_current_email)):
        if not mg_find_user(current_email):
            raise HTTPException(status_code=401, detail="User not found")
        created = mg_add(current_email, payload.note_title, payload.note_description, media=payload.media or [])
        return NoteOut(**created)

    @app.post("/notes/with-media", response_model=NoteOut)
    async def create_note_with_media(
        note_title: str = Form(...),
        note_description: str = Form(...),
        files: List[UploadFile] = File(default=[]),
        current_email: str = Depends(get_current_email)
    ):
        if not mg_find_user(current_email):
            raise HTTPException(status_code=401, detail="User not found")
        saved_media = []
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        for f in files:
            meta, err = await save_upload(UPLOAD_DIR, f)
            if not err:
                saved_media.append(meta)
        created = mg_add(current_email, note_title, note_description, media=saved_media)
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
            "note_title": current.get("note_title"),          # already Base64 in DB
            "note_description": current.get("note_description"),
            "archived_at": datetime.now(timezone.utc),
        }

        updated = notes.find_one_and_update(
            {"uniqueID": unique_id},
            {
                "$push": {"note_history": {"$each": [prev_snapshot], "$position": 0}},
                "$set": {"note_title": b64e(payload.note_title), "note_description": b64e(payload.note_description)}
            },
            return_document=ReturnDocument.AFTER
        )
        updated.pop("_id", None)
        # decode before return
        updated["note_title"] = b64d(updated.get("note_title"))
        updated["note_description"] = b64d(updated.get("note_description"))
        decoded_hist = []
        for h in updated.get("note_history", []):
            decoded_hist.append({
                "note_title": b64d(h.get("note_title","")),
                "note_description": b64d(h.get("note_description","")),
                "archived_at": h.get("archived_at")
            })
        updated["note_history"] = decoded_hist
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
