from pydantic import BaseModel, Field, EmailStr
from datetime import date


class NoteBase(BaseModel):
    task: str
    status: bool
    event_date: date = Field(examples=["2004-05-13"])
    user_id: int


class EditBase(NoteBase):
    event_date: date


class UserBase(BaseModel):
    username: str
    email: EmailStr

class Classified(BaseModel):
    password: str

class Token(BaseModel):
    acess_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class UserInDb(BaseModel):
    hash_password: str