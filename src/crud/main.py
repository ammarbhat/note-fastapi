from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from datetime import datetime, date, timedelta, timezone
from crud.models import Note, User
from crud.schemas import NoteBase, EditBase, UserBase, Classified, TokenData, Token
from crud.database import engine, Base, get_db
from pwdlib import PasswordHash
from jwt.exceptions import InvalidTokenError
from dotenv import load_dotenv
import os
import jwt

app = FastAPI()
Base.metadata.create_all(bind=engine)

load_dotenv()
SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwdhasher = PasswordHash.recommended()
DUMMY_HASH = pwdhasher.hash("dummypassword")


def verify_password(password, hashed_password):
    return pwdhasher.verify(password, hashed_password)


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
        return False
    if not verify_password(password, user.hash_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: Annotated[str, Depends(oauth_scheme)], db=Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


@app.post("/token")
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db=Depends(get_db)
) -> Token:
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="Bearer")


@app.get("/notes")
def all_notes(
    current_user: Annotated[User, Depends(get_current_user)],
    db=Depends(get_db),
    limit: int = 20,
    skip: int = 0,
):
    return db.query(Note).offset(skip).limit(limit).all()


@app.get("/notes/{note_date}")
def notes_by_date(
    note_date: date,
    curr: Annotated[User, Depends(get_current_user)],
    db=Depends(get_db),
):
    notes = db.query(Note).filter(Note.event_date.contains(note_date)).all()
    if len(notes) > 0:
        return notes
    else:
        raise HTTPException(status_code=404, detail="No items found")


@app.post("/notes/")
def post_note(
    note: NoteBase, curr: Annotated[User, Depends(get_current_user)], db=Depends(get_db)
):
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
def delete_note(
    note_id: int, curr: Annotated[User, Depends(get_current_user)], db=Depends(get_db)
):
    note = db.query(Note).filter(Note.id == note_id).first()
    if note is None:
        raise HTTPException(status_code=404, detail="note not found")
    if curr.id != note.user_id:
        raise HTTPException(status_code=403, detail="Not your note")
    db.delete(note)
    db.commit()
    return {"message": "note deleted"}


@app.put("/notes/{note_id}")
def update_note(
    note_id: int,
    edits: EditBase,
    curr: Annotated[User, Depends(get_current_user)],
    db=Depends(get_db),
):
    note = db.query(Note).filter(Note.id == note_id).first()
    if note is None:
        raise HTTPException(status_code=404, detail="note not found")
    if curr.id != note.user_id:
        raise HTTPException(status_code=403, detail="Not your note")
    note.task = edits.task
    note.event_date = edits.event_date
    note.status = edits.status
    db.commit()
    return {"message": "note edited"}


@app.post("/users/")
def add_user(user: UserBase, body: Classified, db=Depends(get_db)):
    new_user = User(
        username=user.username,
        email=user.email,
        hash_password=pwdhasher.hash(body.password),
    )
    test_user = db.query(User).filter(User.username == user.username).first()
    if test_user:
        if user.username == test_user.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="user already exists"
            )
    db.add(new_user)
    db.commit()
    return {"message": "User added"}


@app.get("/users/me")
def get_me(curr: Annotated[User, Depends(get_current_user)], db=Depends(get_db)):
    user = db.query(User).filter(User.username == curr.username).first()
    return user


@app.delete("/users/{username}")
def delete_user(
    username: str,
    body: Classified,
    curr: Annotated[User, Depends(get_current_user)],
    db=Depends(get_db),
):
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    elif not pwdhasher.verify(body.password, user.hash_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid username or password",
        )
    else:
        db.delete(user)
        db.commit()
        return {"message": "User deleted"}
