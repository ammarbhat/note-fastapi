from fastapi import FastAPI, HTTPException, Depends, status
from typing import Annotated
from datetime import datetime, date
from crud.models import Note, User
from crud.schemas import NoteBase, EditBase, UserBase, Classified
from crud.database import engine, Base, get_db
from pwdlib import PasswordHash

app = FastAPI()
Base.metadata.create_all(bind=engine)

pwdhasher = PasswordHash.recommended()
DUMMY_HASH = pwdhasher.hash("dummypassword")

def verify_password(password, hashed_password):
    return pwdhasher.verify(hashed_password, password)

def get_hash(password):
    return pwdhasher.hash(password)

def get_user(db, username: str):
    user = db.query(User).filter(User.username == username).first()
    if user is None:
       return False
    return user

def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        verify_password(password, DUMMY_HASH)
    if not verify_password(password, user.hash_password):
        return False
    return user


@app.get("/notes")
def all_notes(db=Depends(get_db)):
    return db.query(Note).all()


@app.get("/notes/{note_date}")
def notes_by_date(note_date: date, db=Depends(get_db)):
    notes = db.query(Note).filter(Note.event_date.contains(note_date)).all()
    if len(notes) > 0:
        return notes
    else:
        raise HTTPException(status_code=404, detail="No items found")


@app.post("/notes/")
def post_note(note: NoteBase, db=Depends(get_db)):
    new_note = Note(
        task=note.task,
        status=note.status,
        event_date=note.event_date,
        user_id=note.user_id,
    )
    db.add(new_note)
    db.commit()
    return {"message": "note added"}


@app.delete("/notes/{note_id}")
def delete_note(note_id: int, db=Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id).first()
    if note is None:
        raise HTTPException(status_code=404, detail="note not found")
    db.delete(note)
    db.commit()
    return {"message": "note deleted"}


@app.put("/notes/{note_id}")
def update_note(note_id: int, edits: EditBase, db=Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id).first()
    if note is None:
        raise HTTPException(status_code=404, detail="note not found")
    note.task = edits.task
    note.event_date = edits.event_date
    note.status = edits.status
    db.commit()
    return {"message": "note edited"}


@app.post("/users/")
def add_user(user: UserBase,body: Classified, db=Depends(get_db)):
    new_user = User(
        username=user.username,
        email=user.email,
        hash_password=pwdhasher.hash(body.password),
    )
    test_user = db.query(User).filter(User.username == user.username).first()
    if  test_user:
     if user.username == test_user.username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user already exists")
    db.add(new_user)
    db.commit()


@app.delete("/users/{username}")
def delete_user(username: str, body: Classified, db=Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    elif not pwdhasher.verify(body.password, user.hash_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid username or password")
    else:
        db.delete(user)
        db.commit()
        return {"message" : "User deleted"}
