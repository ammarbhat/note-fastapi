from datetime import date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from crud.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str]
    email: Mapped[str]
    hash_password: Mapped[str]

    notes: Mapped[list["Note"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    task: Mapped[str]
    status: Mapped[bool]
    event_date: Mapped[date]

    users: Mapped["User"] = relationship(back_populates="notes")
