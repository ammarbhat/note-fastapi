from datetime import date
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)
from database import Base

class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    task: Mapped[str]
    status: Mapped[bool]
    event_date: Mapped[date]

