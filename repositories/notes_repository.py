from datetime import timezone, datetime
from typing import Dict, Any, List
from pymongo.collection import Collection
from databases.mongodb_connect import get_db
from utils_b64 import b64e, b64d

def _col() -> Collection:
    return get_db()["notes"]

def _serialize(doc: Dict[str, Any]) -> Dict[str, Any]:
    d = dict(doc); d.pop("_id", None); return d

def _next_unique_id() -> int:
    top = _col().find_one({}, sort=[("uniqueID", -1)], projection={"uniqueID": 1})
    return (top["uniqueID"] + 1) if top and "uniqueID" in top else 1

def _decode_note(doc: Dict[str, Any]) -> Dict[str, Any]:
    doc = dict(doc)
    doc["note_title"] = b64d(doc.get("note_title"))
    doc["note_description"] = b64d(doc.get("note_description"))
    doc["note_history"] = [
        {
            "note_title": b64d(h.get("note_title","")),
            "note_description": b64d(h.get("note_description","")),
            "archived_at": h.get("archived_at")
        }
        for h in doc.get("note_history", [])
    ]
    doc["media"] = doc.get("media", [])
    return doc

# === public: only two functions ===

def add_note(owner_email: str, note_title: str, note_description: str, media: List[Dict[str, Any]] | None = None) -> Dict[str, Any]:
    doc = {
        "uniqueID": _next_unique_id(),
        "note_title": b64e(note_title),
        "note_description": b64e(note_description),
        "note_created": datetime.now(timezone.utc),
        "owner_key": owner_email,
        "note_history": [],
        "media": media or [],
    }
    _col().insert_one(doc)
    return _decode_note(_serialize(doc))

def get_all_notes(owner_email: str) -> List[Dict[str, Any]]:
    docs = list(_col().find({"owner_key": owner_email}).sort("uniqueID", 1))
    return [_decode_note(_serialize(d)) for d in docs]
