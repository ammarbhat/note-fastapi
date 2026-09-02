from fastapi.testclient import TestClient
import pytest
from crud.main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from crud.database import Base, get_db
from crud.models import Note
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


app.dependency_overrides[get_db] = override_get_db


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
    note = Note(task="anythings", status=True, event_date=date(2026, 5, 13))
    test_db.add(note)
    test_db.commit()

    response = client.get("/notes/2026-05-13")
    assert response.status_code == 200

def test_note_not_found():
    response = client.get("/notes/2026-05-13")  
    assert response.status_code == 404

def test_create_note():
    response = client.post("/notes/", json={"task": "hey", "status": True, "event_date": "2026-05-13"})
    assert response.status_code == 200
    assert response.json() == {"message" : "note added"}

def test_create_note_invalid_input():
    response = client.post("/notes/", json={ "status": True, "event_date": "2026-05-13"})
    assert response.status_code == 422

def test_put(test_db):
    note = Note(task="anythings", status=True, event_date=date(2026, 5, 13))
    test_db.add(note)
    test_db.commit()
    test_db.refresh(note)

    response = client.put(f"/notes/{note.id}", json={ "task": "hey", "status": True, "event_date": "2026-05-13"})
    assert response.status_code == 200
    assert response.json() == {"message" : "note edited"}

    test_db.refresh(note)
    assert note.task == "hey"

def test_put_invalid():
    response = client.put(f"/notes/1", json={ "task": "hey", "status": True, "event_date": "2026-05-13"})
    assert response.status_code == 404

def test_delete(test_db):
    note = Note(task="anythings", status=True, event_date=date(2026, 5, 13))
    test_db.add(note)
    test_db.commit()
    test_db.refresh(note)

    response = client.delete(f"/notes/{note.id}")
    assert response.status_code == 200

def test_invalid_delete():
    response = client.delete(f"/notes/1")
    assert response.status_code == 404