from datetime import datetime, timezone
from typing import Dict, Any, List

from pymongo.collection import Collection

COLLECTION_NAME = "notes"

def _col(db) -> Collection:
    return db[COLLECTION_NAME]

def _serialize(doc: Dict[str, Any]) -> Dict[str, Any]:
    d = dict(doc)
    d.pop("_id", None)
    return d

def _next_unique_id(db) -> int:
    """
    Increment by looking up the maximum uniqueID (starts at 1 if empty).
    (Simple per your spec; not atomic for concurrent writers.)
    """
    top = _col(db).find_one({}, sort=[("uniqueID", -1)], projection={"uniqueID": 1})
    return (top["uniqueID"] + 1) if top and "uniqueID" in top else 1


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
