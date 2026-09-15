from fastapi.testclient import TestClient
import pytest
from crud.main import app, get_current_user
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from crud.database import Base, get_db
from crud.models import Note, User
from datetime import date
from sqlalchemy.pool import StaticPool

client = TestClient(app)
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
Base.metadata.create_all(bind=engine)
TestingSession = sessionmaker(bind=engine)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    return User(id=1, username="testuser", email="test@test.com", hash_password="fake")


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


@pytest.fixture
def test_db():
    db = TestingSession()
    yield db
    db.query(Note).delete()
    db.commit()
    db.close()


def test_all_notes():
    response = client.get("/notes")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_notes_by_date(test_db):
    note = Note(task="anythings", status=True, event_date=date(2026, 5, 13), user_id=1)
    test_db.add(note)
    test_db.commit()

    response = client.get("/notes/2026-05-13")
    assert response.status_code == 200


def test_note_not_found():
    response = client.get("/notes/2026-05-13")
    assert response.status_code == 404


def test_create_note(test_db):
    response = client.post(
        "/notes/",
        json={"task": "hey", "status": True, "event_date": "2026-05-13", "user_id": 1},
    )
    assert response.status_code == 200
    assert response.json() == {"message": "note added"}


def test_create_note_invalid_input():
    response = client.post(
        "/notes/", json={"status": True, "event_date": "2026-05-13", "user_id": 1}
    )
    assert response.status_code == 422


def test_put(test_db):
    note = Note(task="anythings", status=True, event_date=date(2026, 5, 13), user_id=1)
    test_db.add(note)
    test_db.commit()
    test_db.refresh(note)

    response = client.put(
        f"/notes/{note.id}",
        json={"task": "hey", "status": True, "event_date": "2026-05-13", "user_id": 1},
    )
    assert response.status_code == 200
    assert response.json() == {"message": "note edited"}

    test_db.refresh(note)
    assert note.task == "hey"


def test_put_invalid():
    response = client.put(
        f"/notes/1",
        json={"task": "hey", "status": True, "event_date": "2026-05-13", "user_id": 1},
    )
    assert response.status_code == 404


def test_delete(test_db):
    note = Note(task="anythings", status=True, event_date=date(2026, 5, 13), user_id=1)

    test_db.add(note)
    test_db.commit()
    test_db.refresh(note)

    response = client.delete(f"/notes/{note.id}")
    assert response.status_code == 200


def test_invalid_delete():
    response = client.delete(f"/notes/1")
    assert response.status_code == 404


def test_add_user(test_db):
    response = client.post(
        "/users/",
        json={
            "user": {"username": "string", "email": "user@example.com"},
            "body": {"password": "stringis13"},
        },
    )

    assert response.status_code == 200


def test_add_user_invalid_email(test_db):
    response = client.post(
        "/users/",
        json={
            "user": {"username": "string", "email": "com"},
            "body": {"password": "stringis13"},
        },
    )

    assert response.status_code == 422


def test_add_user_existing_username(test_db):
    user = User(
        username="anythings", email="string@example.com", hash_password="hjxalsjkdfh123"
    )
    test_db.add(user)
    test_db.commit()

    response = client.post(
        "/users/",
        json={
            "user": {"username": "anythings", "email": "user@example.com"},
            "body": {"password": "stringis13"},
        },
    )

    assert response.status_code == 400


def test_delete_user(test_db):
    user = User(
        username="anythingss",
        email="string@example.com",
        hash_password="$argon2id$v=19$m=65536,t=3,p=4$THQbKxu08x6oCW89/m1vWQ$k94PQ0X2lcuyzJi6H1/2QqczkLK0fTZ7b3rZTn3oQsA",
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    response = client.request(
        "DELETE", f"/users/{user.username}", json={"password": "stringis13"}
    )

    assert response.status_code == 200
