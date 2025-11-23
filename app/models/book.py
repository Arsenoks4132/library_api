from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database.session import Base

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    author_id = Column(Integer, ForeignKey("authors.id"), nullable=False)
    description = Column(Text)
    year = Column(Integer)
    isbn = Column(String(13), unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    author = relationship("Author", back_populates="books")