from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class NoteMedia(BaseModel):
    url: str
    mime_type: str
    size_bytes: int
    original_name: str

class NoteSnapshot(BaseModel):
    note_title: str
    note_description: str
    archived_at: datetime

class NoteCreate(BaseModel):
    note_title: str = Field(..., min_length=1)
    note_description: str = Field(..., min_length=1)
    media: List[NoteMedia] = []

class NoteUpdate(BaseModel):
    note_title: str = Field(..., min_length=1)
    note_description: str = Field(..., min_length=1)

class NoteOut(BaseModel):
    uniqueID: int
    note_title: str
    note_description: str
    note_created: datetime
    owner_key: str
    note_history: List[NoteSnapshot] = []
    media: List[NoteMedia] = []
