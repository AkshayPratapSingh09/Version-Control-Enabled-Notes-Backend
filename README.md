# 📝 FastAPI Notes — A Modern Note Taking App with Version Control

<p align="center">
  <img src="https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png" alt="FastAPI Logo" width="150"/>
  <br/>
  <b>A blazing-fast and elegant note-taking API built with FastAPI and MongoDB, featuring full CRUD operations and version control.</b>
</p>

---

## 🚀 Overview

**FastAPI Notes** is a modern backend service that lets you **create**, **read**, **update**, and **delete** notes — with built-in **version history tracking**.  
It’s designed for developers and teams who want to manage note revisions with the same flexibility as code commits.

### ✨ Key Features
- ⚡ **Fast & Async** — Built with FastAPI for ultra-fast responses.
- 🗂️ **Full CRUD Support** — Create, read, update, and delete notes easily.
- 🔄 **Version Control** — Track every change and revert to previous versions.
- 🔒 **RESTful & Extensible** — Clean endpoints, easily integrable with any frontend.
- 🧠 **JSON-based API** — Ideal for modern web and mobile applications.

---

## 🧰 Tech Stack

| Layer | Technology |
|:------|:------------|
| Backend Framework | [FastAPI](https://fastapi.tiangolo.com/) |
| Database | [MongoDB](https://www.mongodb.com/) or SQLite (optional) |
| ORM / ODM | [Motor](https://motor.readthedocs.io/) |
| API Docs | Swagger / ReDoc (auto-generated) |
| Language | Python 3.10+ |
| Versioning | Custom version control model |

---

## 🏗️ Project Structure

```
fastapi-notes/
├─ app.py
├─ auth.py
├─ utils.py
├─ utils_b64.py
├─ utils_media.py
├─ requirements.txt
├─ README.md
├─ models/
│  ├─ auth_models.py
│  ├─ notes.py
│  └─ sql_models.py
├─ databases/
│  ├─ mongodb_connect.py
│  └─ sql_connect.py
├─ repositories/
│  ├─ notes_repository.py          
get_all_notes
│  ├─ sql_notes_repository.py      
get_all_notes
│  ├─ users_repository.py          
│  └─ sql_users_repository.py      
└─ scripts/
   ├─ migrate_to_base64_mongo.py
   └─ migrate_to_base64_sql.py

```
---

## ⚙️ Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/fastapi-notes.git
cd fastapi-notes
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate    # For Linux/Mac
venv\Scripts\activate       # For Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Environment Variables
Copy `.env.example` to `.env` and configure your MongoDB URI:
```bash
MONGO_URI=mongodb://localhost:27017
DB_NAME=notes_db
```

### 5. Run the Server
```bash
uvicorn app:app --reload
```

The API will be available at `http://localhost:8000`

---

## 📖 API Documentation & Usage

FastAPI automatically generates interactive API documentation. Access it here:
- **Swagger UI** → [http://localhost:8000/docs](http://localhost:8000/docs) *(Recommended)*
- **ReDoc** → [http://localhost:8000/redoc](http://localhost:8000/redoc)

### 🎯 Using Swagger UI (Step-by-Step Guide)

#### **First Time Setup**
1. **Start the server** with `uvicorn app:app --reload`
2. **Open Swagger UI** at [http://localhost:8000/docs](http://localhost:8000/docs)
3. **Register a new account** using the `/auth/register` endpoint
4. **Login** to get your access token
5. **Authorize** your session using the 🔒 button in Swagger UI

#### **Authentication Flow**

**Step 1: Register a New User**
- Click on `POST /auth/register`
- Click "Try it out"
- Use this example payload:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Step 2: Login to Get Access Token**
- Click on `POST /auth/login`
- Click "Try it out"
- Enter credentials:
  - `username`: `user@example.com`
  - `password`: `securepassword123`
- Copy the `access_token` from the response

**Step 3: Authorize Your Session**
- Click the 🔒 **Authorize** button at the top of Swagger UI
- Enter: `Bearer YOUR_ACCESS_TOKEN_HERE`
- Click "Authorize"

#### **Working with Notes**

**Create a Simple Note**
- Use `POST /notes` with this payload:
```json
{
  "note_title": "My First Note",
  "note_description": "This is a sample note created via Swagger UI"
}
```

**Create a Note with Media**
- Use `POST /notes/with-media` (multipart form)
- Fill in:
  - `note_title`: "Note with Image"
  - `note_description`: "This note has an attached image"
  - `files`: Upload an image file (max 5MB)

**List All Your Notes**
- Use `GET /notes` (no payload needed)

**Update a Note**
- Use `PUT /notes/{unique_id}` with:
```json
{
  "note_title": "Updated Note Title",
  "note_description": "Updated content here"
}
```

**Upload Media Files**
- Use `POST /media/upload`
- Select multiple files (images/videos, max 5MB each)
- Supported formats: JPEG, PNG, GIF, WebP, MP4, WebM, MOV

#### **Understanding API Responses**

**Successful Note Creation Response:**
```json
{
  "uniqueID": 1,
  "note_title": "My First Note",
  "note_description": "This is a sample note",
  "note_created": "2025-10-31T10:30:00Z",
  "owner_key": "user@example.com",
  "note_history": [],
  "media": []
}
```

**Media Upload Response:**
```json
{
  "saved": [
    {
      "url": "/uploads/image_20251031_103000.jpg",
      "mime_type": "image/jpeg",
      "size_bytes": 245760,
      "original_name": "photo.jpg"
    }
  ],
  "errors": [],
  "limit_bytes": 5242880,
  "allowed": ["image/jpeg", "image/png", "video/mp4"]
}
```

#### **Common Parameters Explained**

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `unique_id` | integer | Note identifier for updates/deletes | `1`, `42`, `123` |
| `note_title` | string | Title of your note | `"Meeting Notes"` |
| `note_description` | string | Main content of your note | `"Discussed project timeline"` |
| `files` | file[] | Media files to upload | Select from file picker |
| `Authorization` | header | Bearer token for authentication | `Bearer eyJ0eXAiOiJKV1Q...` |

#### **Error Handling Examples**

**401 Unauthorized** - Missing or invalid token:
```json
{
  "detail": "Not authenticated"
}
```

**404 Not Found** - Note doesn't exist:
```json
{
  "detail": "Note not found"
}
```

**413 File Too Large** - Media file exceeds 5MB:
```json
{
  "saved": [],
  "errors": [
    {
      "file": "large_video.mp4",
      "error": "File too large (max 5MB)"
    }
  ]
}
```

---
## 🖼️ Media Uploads (Optional, 5 MB/file)

- Supported types: **images** (jpeg, png, gif, webp) and **videos** (mp4, webm, mov).
- **Strict limit:** 5 MB per file. Larger files are skipped with a warning; the request still succeeds.
- Files are stored under `UPLOAD_DIR` (default: `./uploads`) and served at `/uploads/...`.

---

### Endpoints
- `POST /media/upload` (Bearer token required)  
  Multipart field: `files` (one or many). Returns `{ saved: [...], errors: [...] }`.
- `POST /notes`  
  JSON body supports optional `media: [{ url, mime_type, size_bytes, original_name }]`.  
  Use after uploading files to `/media/upload`.
- `POST /notes/with-media`  
  Multipart form: `note_title`, `note_description`, `files[]`. Uploads and attaches in one step.

> Media is **not Base64 encoded**. Only note `title`/`description` are stored as Base64.  
> Existing notes remain valid; `media` defaults to an empty list.

---

## 🔐 Base64 Storage & Migration

This API **stores notes in Base64** (UTF-8 → Base64 in DB) and **decodes on responses**.  
Why? Safer transport, no encoding surprises, and consistent cross-DB behavior.

### What’s encoded
- `note_title`
- `note_description`
- (Mongo only) `note_history[*].note_title`, `note_history[*].note_description`

### New installs (fresh DB)
No action needed. The repositories encode on write and decode on read automatically.

### Migrate an existing database

> **Backup first!** Always snapshot your DB before migrations.

#### MongoDB
```bash
export MONGO_URI="mongodb://localhost:27017"
export DB_NAME="notes_db"
python scripts/migrate_to_base64_mongo.py


---



## 🧬 Version Control Logic

Each note update automatically creates a new version entry:
```json
{
  "note_id": "123abc",
  "title": "Meeting Notes",
  "content": "Discussed project timeline",
  "version": 3,
  "updated_at": "2025-10-31T10:00:00Z"
}
```
You can easily revert to an older version via the `/notes/{id}/versions/{version_id}` endpoint.

---

## 🤝 Contributing

Contributions are welcome!  
Follow these steps to contribute:

1. **Fork** the repository  
2. **Create** a new branch (`git checkout -b feature-name`)  
3. **Commit** changes (`git commit -m "feat: add feature-name"`)  
4. **Push** to your fork (`git push origin feature-name`)  
5. **Submit a Pull Request**

Please follow [Conventional Commits](https://www.conventionalcommits.org/) format.

---

## 👨‍💻 Maintainers

| Name | Role | GitHub |
|:------|:------|:-------|
| Arpan Singh | Lead Developer | [@yourusername](https://github.com/yourusername) |

---

## 🧠 Future Enhancements
- 🧩 User authentication (JWT-based)
- 🌐 Multi-user collaboration
- 💾 Export/Import notes
- ☁️ Cloud deployment via Docker

---

## 📜 License
This project is licensed under the **MIT License** — feel free to use and modify it.

---

<p align="center">
  Made with ❤️ using <b>FastAPI</b> and Python.
</p>
