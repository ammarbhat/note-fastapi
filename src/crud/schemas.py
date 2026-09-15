from pydantic import BaseModel, Field, EmailStr, field_validator
from datetime import date


def check_password(pwd):
    if len(pwd) < 8 or pwd.isalpha() or pwd.isdigit() or pwd.isspace() or len(pwd) > 21:
        return False
    return True


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

    @field_validator("password")
    @classmethod
    def validate(cls, v):
        if not check_password(v):
            raise ValueError(
                "password must be 8+ characters and not entirely letters, digits, or whitespace"
            )
        return v


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserInDb(BaseModel):
    hash_password: str
