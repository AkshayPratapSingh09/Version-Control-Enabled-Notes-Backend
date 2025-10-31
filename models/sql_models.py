from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from databases.sql_connect import Base

class Note(Base):
    __tablename__ = "notes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)  # uniqueID
    note_title: Mapped[str] = mapped_column(String(512), nullable=False)
    note_description: Mapped[str] = mapped_column(String, nullable=False)
    note_created: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    history = relationship("NoteHistory", back_populates="note", cascade="all, delete-orphan", order_by="NoteHistory.id.desc()")

class NoteHistory(Base):
    __tablename__ = "note_history"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    note_id: Mapped[int] = mapped_column(ForeignKey("notes.id", ondelete="CASCADE"), nullable=False)
    note_title: Mapped[str] = mapped_column(String(512), nullable=False)
    note_description: Mapped[str] = mapped_column(String, nullable=False)
    archived_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    note = relationship("Note", back_populates="history")
