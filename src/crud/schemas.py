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
    password: str

class DeleteRequest(BaseModel):
    password: str