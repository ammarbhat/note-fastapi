from fastapi import FastAPI, HTTPException, Depends
from typing import Annotated
from pydantic import BeforeValidator
from datetime import datetime, date
from models import Note
from schemas import NoteBase
from database import engine, Base, get_db


app = FastAPI()
Base.metadata.create_all(bind=engine)


@app.get("/notes")
def hello():
    return {"message": "under construction"}


@app.get("/notes/{date}")
def notes_by_date(date: date, db=Depends(get_db)):
    notes = []
    notes.append(db.query(Note).filter(Note.event_date.contains(date)).all())
    if len(notes) > 0:
        return db.query(Note).filter(Note.event_date.contains(date)).all()
    else:
        raise HTTPException(status_code=404, detail="No items found")


@app.post("/notes/")
def post_note(note: NoteBase, db=Depends(get_db)):
    new_note = Note(task=note.task, status=note.status, event_date=note.event_date)
    db.add(new_note)
    db.commit()



