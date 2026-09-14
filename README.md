# Notes API (FastAPI + SQLAlchemy + JWT Auth)

A simple CRUD API for managing dated notes/tasks, built with FastAPI and SQLAlchemy, secured with JWT-based authentication.

## Features

- **User accounts** — create and delete users, with passwords hashed via `pwdlib` (Argon2).
- **JWT authentication** — OAuth2 password flow (`/token`) issues short-lived Bearer access tokens.
- **Notes CRUD** — create, read (all / by date), update, and delete notes, each tied to a user.
- **SQLite persistence** via SQLAlchemy ORM, with a separate in-memory test database.
- **Pytest test suite** covering the notes endpoints.

## Tech Stack

- [FastAPI](https://fastapi.tiangolo.com/) (`fastapi[standard]`)
- [SQLAlchemy](https://www.sqlalchemy.org/) 2.x (typed `Mapped` models)
- [PyJWT](https://pyjwt.readthedocs.io/) for token encoding/decoding
- [pwdlib](https://frankie567.github.io/pwdlib/) (Argon2) for password hashing
- SQLite as the database
- pytest + FastAPI's `TestClient` for testing
- Managed with [uv](https://docs.astral.sh/uv/)

## Project Structure

```
note-fastapi/
├── pyproject.toml
└── src/
    └── crud/
        ├── main.py         # FastAPI app, auth logic, all routes
        ├── models.py       # SQLAlchemy models (User, Note)
        ├── schemas.py      # Pydantic request/response schemas
        ├── database.py     # Engine, session, Base, get_db dependency
        └── tests/
            └── test_main.py
```

## Data Model

- **User**: `id`, `username`, `email`, `hash_password` — has many `Note`s (cascade delete).
- **Note**: `id`, `task`, `status` (bool), `event_date`, `user_id` (FK to `User`).

## Setup

```bash
# clone the repo
git clone https://github.com/ammarbhat/note-fastapi.git
cd note-fastapi

# install dependencies (using uv)
uv sync

# run the dev server
uv run fastapi dev src/crud/main.py
```

The API will be available at `http://127.0.0.1:8000`, with interactive docs at `/docs`.

## Authentication

All notes and most user endpoints require a valid Bearer token.

1. **Create a user**
   ```
   POST /users/
   { "user": { "username": "...", "email": "..." }, "body": { "password": "..." } }
   ```
2. **Get a token**
   ```
   POST /token
   (form data: username, password)
   ```
3. **Use the token** on subsequent requests:
   ```
   Authorization: Bearer <access_token>
   ```

Tokens are signed with HS256 and expire after 30 minutes.

## Endpoints

| Method | Path              | Auth required | Description                          |
|--------|-------------------|:--------------:|--------------------------------------|
| POST   | `/token`          | No             | Log in, get an access token          |
| POST   | `/users/`         | No             | Create a new user                    |
| DELETE | `/users/{username}` | Yes          | Delete a user (requires password)    |
| GET    | `/notes`          | Yes            | List all notes                       |
| GET    | `/notes/{date}`   | Yes            | List notes for a specific date       |
| POST   | `/notes/`         | Yes            | Create a note                        |
| PUT    | `/notes/{id}`     | Yes            | Edit a note                          |
| DELETE | `/notes/{id}`     | Yes            | Delete a note (only if you own it)   |

## Running Tests

```bash
uv run pytest
```

Tests use an in-memory SQLite database and override `get_db` and `get_current_user` so the suite runs without needing a real login flow.

## Notes / Known Limitations

- The JWT `SECRET_KEY` is currently hardcoded in `main.py` — move this to an environment variable before deploying anywhere real.
- `update_note` and `notes_by_date`/`all_notes` don't yet scope results to the requesting user, so any authenticated user can view/edit any note (only `delete_note` currently checks ownership).
- No token refresh flow yet — tokens simply expire after 30 minutes and require a new login.
