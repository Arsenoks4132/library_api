from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class BookBase(BaseModel):
    title: str
    author_id: int
    description: Optional[str] = None
    year: Optional[int] = None
    isbn: Optional[str] = None

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author_id: Optional[int] = None
    description: Optional[str] = None
    year: Optional[int] = None
    isbn: Optional[str] = None

class BookResponse(BookBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
