from sqlalchemy.orm import Session
from ..models.author import Author
from ..schemas.author import AuthorCreate

def get_authors(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Author).offset(skip).limit(limit).all()

def get_author_books(db: Session, author_id: int):
    author = db.query(Author).filter(Author.id == author_id).first()
    return author.books if author else []

def create_author(db: Session, author: AuthorCreate):
    db_author = Author(**author.dict())
    db.add(db_author)
    db.commit()
    db.refresh(db_author)
    return db_author
