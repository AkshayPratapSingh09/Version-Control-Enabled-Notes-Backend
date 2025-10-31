from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class NoteSnapshot(BaseModel):
    note_title: str
    note_description: str
    archived_at: datetime

class NoteCreate(BaseModel):
    note_title: str = Field(..., min_length=1)
    note_description: str = Field(..., min_length=1)

class NoteUpdate(BaseModel):
    note_title: str = Field(..., min_length=1)
    note_description: str = Field(..., min_length=1)

class NoteOut(BaseModel):
    uniqueID: int
    note_title: str
    note_description: str
    note_created: datetime
    note_history: List[NoteSnapshot] = []
