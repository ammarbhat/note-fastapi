# Notes API

A CRUD API for managing notes, built with FastAPI and SQLAlchemy (SQLite). Fully tested with pytest.

## Features

- Create, read, update, and delete notes
- Filter notes by event date
- Each note has a task, status, and event date
- Full pytest test suite covering success and failure (404) cases for every endpoint, using an isolated in-memory test database

## Tech Stack

- **FastAPI** – web framework
- **SQLAlchemy** – ORM for database access
- **SQLite** – database
- **pytest** – testing

## Endpoints

| Method | Path                | Description              |
|--------|---------------------|--------------------------|
| GET    | `/notes`            | Get all notes            |
| GET    | `/notes/{note_date}`| Get notes by event date  |
| POST   | `/notes/`           | Create a new note        |
| PUT    | `/notes/{note_id}`  | Update an existing note  |
| DELETE | `/notes/{note_id}`  | Delete a note            |

## Running Locally

```bash
uv sync
uv run uvicorn main:app --reload
```

Then visit `http://127.0.0.1:8000/docs` for interactive API docs (Swagger UI).

## Running Tests

```bash
uv run pytest
```

Tests run against an isolated in-memory SQLite database, so your real `notes.db` is never touched.