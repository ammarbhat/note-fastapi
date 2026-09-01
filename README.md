# Notes API

A simple CRUD API for managing notes, built with FastAPI and SQLAlchemy (SQLite).

## Features

- Create, read, update, and delete notes
- Filter notes by date
- Each note has a task, status, and event date

## Tech Stack

- **FastAPI** – web framework
- **SQLAlchemy** – ORM for database access
- **SQLite** – database

## Endpoints

| Method | Path              | Description              |
|--------|-------------------|--------------------------|
| GET    | `/notes`          | Get all notes            |
| GET    | `/notes/{date}`   | Get notes by event date  |
| POST   | `/notes/`         | Create a new note        |
| PUT    | `/notes/{note_id}`| Update an existing note  |
| DELETE | `/notes/{note_id}`| Delete a note            |

## Running Locally

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Then visit `http://127.0.0.1:8000/docs` for interactive API docs (Swagger UI).