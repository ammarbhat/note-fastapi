from pydantic import BaseModel, Field
from datetime import date
class NoteBase(BaseModel):
    task : str 
    status : bool
    event_date : date = Field(examples=["2004-05-13"])