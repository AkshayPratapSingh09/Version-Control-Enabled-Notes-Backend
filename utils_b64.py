import base64

def b64e(txt: str) -> str:
    if txt is None:
        return ""
    return base64.b64encode(txt.encode("utf-8")).decode("ascii")

def b64d(txt: str) -> str:
    if not txt:
        return ""
    try:
        return base64.b64decode(txt.encode("ascii")).decode("utf-8")
    except Exception:
        return txt

def is_b64(txt: str) -> bool:
    if not txt:
        return False
    try:
        return b64e(b64d(txt)) == txt
    except Exception:
        return False
