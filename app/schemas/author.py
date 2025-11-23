from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

class AuthorBase(BaseModel):
    name: str
    bio: Optional[str] = None
    birth_date: Optional[date] = None

class AuthorCreate(AuthorBase):
    pass

class AuthorResponse(AuthorBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True