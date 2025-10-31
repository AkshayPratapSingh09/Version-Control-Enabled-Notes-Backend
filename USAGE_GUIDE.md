# ⚡ FastAPI Notes API Usage Guide

This document explains how to interact with the **FastAPI Notes** backend service using its automatically generated Swagger (OpenAPI) documentation and direct API calls.

## 1. Accessing the Interactive Docs

The FastAPI framework automatically generates interactive API documentation powered by Swagger UI.

* **Location:** Once the server is running (typically at `http://localhost:8000`), navigate to:
    * **Swagger UI:** `http://localhost:8000/docs`
    * **ReDoc:** `http://localhost:8000/redoc`

* **Usage:** Use the Swagger UI page to view all available endpoints, required request bodies (schemas), and test calls directly from your browser.

## 2. API Endpoints and Examples (CRUD)

The core functionality revolves around the `/notes` resource for managing notes and their history.

### A. Create a New Note (POST)

Creates a new note entry. The API requires a JSON **payload** containing a `title` and `content`.

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `title` | string | Yes | The title of the new note. |
| `content` | string | Yes | The primary text content of the note. |

**Example Request:**

```bash
# Replace <SERVER_URL> with http://localhost:8000 or your deployment URL
curl -X POST "<SERVER_URL>/notes/" \
     -H "Content-Type: application/json" \
     -d '{"title": "First Meeting Agenda", "content": "Review Q4 goals and Hacktoberfest submissions."}'