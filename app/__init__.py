from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from .database.session import get_db
from .models.book import Book
from .models.author import Author
from .schemas.book import BookCreate, BookResponse, BookUpdate
from .schemas.author import AuthorCreate, AuthorResponse
from .crud.book import (
    get_books, 
    get_book, 
    create_book, 
    update_book, 
    delete_book,
    search_books_by_title
)
from .crud.author import get_authors, get_author_books, create_author

app = FastAPI(title="Library Management API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running successfully"}

# Book endpoints
@app.get("/books", response_model=List[BookResponse])
async def read_books(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    return get_books(db, skip=skip, limit=limit)

@app.get("/books/{book_id}", response_model=BookResponse)
async def read_book(book_id: int, db: Session = Depends(get_db)):
    db_book = get_book(db, book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book

@app.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def add_book(book: BookCreate, db: Session = Depends(get_db)):
    return create_book(db, book)

@app.put("/books/{book_id}", response_model=BookResponse)
async def update_book_info(
    book_id: int, 
    book: BookUpdate, 
    db: Session = Depends(get_db)
):
    db_book = update_book(db, book_id, book)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book

@app.delete("/books/{book_id}")
async def remove_book(book_id: int, db: Session = Depends(get_db)):
    success = delete_book(db, book_id)
    if not success:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Book deleted successfully"}

# Author endpoints
@app.get("/authors", response_model=List[AuthorResponse])
async def read_authors(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    return get_authors(db, skip=skip, limit=limit)

@app.get("/authors/{author_id}/books", response_model=List[BookResponse])
async def read_author_books(author_id: int, db: Session = Depends(get_db)):
    return get_author_books(db, author_id)

@app.post("/authors", response_model=AuthorResponse, status_code=status.HTTP_201_CREATED)
async def add_author(author: AuthorCreate, db: Session = Depends(get_db)):
    return create_author(db, author)

# Search endpoint
@app.get("/books/search/{title}", response_model=List[BookResponse])
async def search_books(title: str, db: Session = Depends(get_db)):
    return search_books_by_title(db, title)


