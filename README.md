# Notes API

A CRUD API for managing notes, built with **FastAPI** and **SQLAlchemy** (SQLite), with **JWT-based user authentication**. Fully tested with pytest.

## Features

- User registration and secure password hashing (`pwdlib`)
- OAuth2 password-flow login issuing JWT access tokens
- Authenticated CRUD for notes: create, read, update, delete
- Filter notes by event date
- Each note has a task, status, and event date, and is tied to the user who owns it
- User deletion (password-protected)
- Full pytest test suite covering success and failure cases (404, 422, 401) for every endpoint, using an isolated in-memory test database

## Tech Stack

- **FastAPI** – web framework
- **SQLAlchemy** – ORM for database access
- **SQLite** – database
- **pwdlib** – password hashing
- **PyJWT** – JSON Web Token creation/validation
- **python-dotenv** – loads secrets from a local `.env` file
- **pytest** – testing

## Setup

1. Clone the repo and install dependencies:

   ```bash
   uv sync
   ```

2. Create a `.env` file in the project root with your own secret key:

   ```
   SECRET_KEY=your-secret-key-here
   ```

   A `.env.example` is included as a template. Never commit your real `.env` — it's already in `.gitignore`.

## Endpoints

### Auth

| Method | Path      | Description                                  |
| ------ | --------- | --------------------------------------------- |
| POST   | `/token`  | Log in with username/password, get a JWT      |

### Users

| Method | Path                | Description                          |
| ------ | ------------------- | ------------------------------------- |
| POST   | `/users/`            | Register a new user                   |
| DELETE | `/users/{username}`  | Delete a user (requires auth + password) |

### Notes

*All notes endpoints require a valid Bearer token from `/token`.*

| Method | Path                 | Description              |
| ------ | -------------------- | ------------------------- |
| GET    | `/notes`             | Get all notes             |
| GET    | `/notes/{note_date}` | Get notes by event date   |
| POST   | `/notes/`            | Create a new note         |
| PUT    | `/notes/{note_id}`   | Update an existing note   |
| DELETE | `/notes/{note_id}`   | Delete a note (owner only) |

## Running Locally

```bash
uv sync
uv run uvicorn main:app --reload
```

Then visit `http://127.0.0.1:8000/docs` for interactive API docs (Swagger UI), where you can register a user, log in via the `/token` endpoint, and authorize requests with the returned Bearer token.

## Running Tests

```bash
uv run pytest
```

Tests run against an isolated in-memory SQLite database, so your real `notes.db` is never touched. Authentication is mocked in tests via a dependency override, so note/user endpoint tests don't require a real login flow.

