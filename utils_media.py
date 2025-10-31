import os, uuid, pathlib
from typing import Tuple, Optional, Dict
from fastapi import UploadFile

ALLOWED_MIME = {
    "image/jpeg", "image/png", "image/gif", "image/webp",
    "video/mp4", "video/webm", "video/quicktime",
}
MAX_BYTES = 5 * 1024 * 1024  # 5MB

def ensure_dir(path: str) -> None:
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)

def guess_subdir(mime: str) -> str:
    return "images" if mime.startswith("image/") else "videos"

def safe_ext(filename: str) -> str:
    ext = pathlib.Path(filename).suffix.lower()
    return ext if ext in {".jpg",".jpeg",".png",".gif",".webp",".mp4",".webm",".mov"} else ""

async def save_upload(base_dir: str, file: UploadFile) -> Tuple[Optional[Dict], Optional[str]]:
    mime = (file.content_type or "").lower()
    if mime not in ALLOWED_MIME:
        return None, f"unsupported content-type: {mime}"

    ext = safe_ext(file.filename or "")
    sub = guess_subdir(mime)
    ensure_dir(os.path.join(base_dir, sub))
    fname = f"{uuid.uuid4().hex}{ext or ''}"
    abs_path = os.path.join(base_dir, sub, fname)

    total = 0
    try:
        with open(abs_path, "wb") as out:
            while True:
                chunk = await file.read(1024 * 1024)  # 1MB chunks
                if not chunk:
                    break
                total += len(chunk)
                if total > MAX_BYTES:
                    out.close()
                    try: os.remove(abs_path)
                    except: pass
                    return None, "file too large (>5MB)"
                out.write(chunk)
    except Exception as e:
        try: os.remove(abs_path)
        except: pass
        return None, f"write error: {e}"

    rel_url = f"/uploads/{sub}/{fname}"
    meta = {
        "url": rel_url,
        "mime_type": mime,
        "size_bytes": total,
        "original_name": file.filename or fname,
    }
    return meta, None
