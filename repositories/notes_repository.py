
from datetime import timezone, datetime
from typing import Dict, Any, List
from pymongo.collection import Collection
from databases.mongodb_connect import get_db

def _col() -> Collection:
    return get_db()["notes"]

def _serialize(doc: Dict[str, Any]) -> Dict[str, Any]:
    d = dict(doc); d.pop("_id", None); return d

def _next_unique_id() -> int:
    top = _col().find_one({}, sort=[("uniqueID", -1)], projection={"uniqueID": 1})
    return (top["uniqueID"] + 1) if top and "uniqueID" in top else 1

def add_note(owner_email: str, note_title: str, note_description: str) -> Dict[str, Any]:
    doc = {
        "uniqueID": _next_unique_id(),
        "note_title": note_title,
        "note_description": note_description,
        "note_created": datetime.now(timezone.utc),
        "owner_key": owner_email,
        "note_history": [],
    }
    _col().insert_one(doc)
    return _serialize(doc)

def get_all_notes(owner_email: str) -> List[Dict[str, Any]]:
    docs = list(_col().find({"owner_key": owner_email}).sort("uniqueID", 1))
    return [_serialize(d) for d in docs]
