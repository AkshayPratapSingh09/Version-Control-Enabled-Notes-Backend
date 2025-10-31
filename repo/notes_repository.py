from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pymongo.collection import Collection

COLLECTION_NAME = "notes"

def _col(db) -> Collection:
    return db[COLLECTION_NAME]

def _serialize(doc: Dict[str, Any]) -> Dict[str, Any]:
    d = dict(doc)
    d.pop("_id", None)
    return d

def _next_unique_id(db) -> int:
    top = _col(db).find_one({}, sort=[("uniqueID", -1)], projection={"uniqueID": 1})
    return (top["uniqueID"] + 1) if top and "uniqueID" in top else 1

# --- Existing (read/write) ---
def add_note(db, note_title: str, note_description: str) -> Dict[str, Any]:
    doc = {
        "uniqueID": _next_unique_id(db),
        "note_title": note_title,
        "note_description": note_description,
        "note_created": datetime.now(timezone.utc),
        "note_history": [],
    }
    _col(db).insert_one(doc)
    return _serialize(doc)

def get_all_notes(db) -> List[Dict[str, Any]]:
    docs = list(_col(db).find({}, sort=[("uniqueID", 1)]))
    return [_serialize(d) for d in docs]

# --- NEW: Edit (Update) with version history ---
def update_note(db, unique_id: int, note_title: str, note_description: str) -> Optional[Dict[str, Any]]:
    now = datetime.now(timezone.utc)
    current = _col(db).find_one({"uniqueID": unique_id})
    if not current:
        return None

    prev_snapshot = {
        "note_title": current.get("note_title"),
        "note_description": current.get("note_description"),
        "archived_at": now,
    }

    _col(db).update_one(
        {"uniqueID": unique_id},
        {
            # newest previous snapshot at head (index 0)
            "$push": {"note_history": {"$each": [prev_snapshot], "$position": 0}},
            "$set": {
                "note_title": note_title,
                "note_description": note_description,
            },
        },
    )
    updated = _col(db).find_one({"uniqueID": unique_id})
    return _serialize(updated)

# --- NEW: Delete ---
def delete_note(db, unique_id: int) -> bool:
    res = _col(db).delete_one({"uniqueID": unique_id})
    return res.deleted_count == 1
