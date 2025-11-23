from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional

from .database.session import get_db, engine, Base
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

# Кастомная конфигурация OpenAPI для улучшенной ReDoc документации
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Library Management API",
        version="1.0.0",
        description="""
        ## 📚 REST API для системы управления библиотекой
        
        Полнофункциональное API для управления книгами и авторами в библиотеке.
        
        ### Основные возможности:
        - 📖 Управление книгами (CRUD операции)
        - 👨‍💼 Управление авторами
        - 🔍 Поиск книг по названию
        - 📄 Пагинация для больших списков
        - ✅ Валидация данных
        
        ### Примеры использования:
        
        **Создание автора:**
        ```json
        {
          "name": "Лев Толстой",
          "bio": "Русский писатель",
          "birth_date": "1828-09-09"
        }
        ```
        
        **Создание книги:**
        ```json
        {
          "title": "Война и мир",
          "author_id": 1,
          "description": "Роман-эпопея",
          "year": 1869,
          "isbn": "9781234567890"
        }
        ```
        """,
        routes=app.routes,
    )
    
    # Кастомизация схемы OpenAPI для лучшего отображения в ReDoc
    openapi_schema["info"]["contact"] = {
        "name": "Поддержка API",
        "email": "support@library.com",
    }
    openapi_schema["info"]["license"] = {
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    }
    
    # Добавляем теги для группировки endpoint-ов
    openapi_schema["tags"] = [
        {
            "name": "books",
            "description": "Операции с книгами: создание, чтение, обновление, удаление книг"
        },
        {
            "name": "authors", 
            "description": "Операции с авторами: создание, чтение, получение книг автора"
        },
        {
            "name": "search",
            "description": "Поисковые операции"
        },
        {
            "name": "health",
            "description": "Проверка работоспособности API"
        }
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app = FastAPI(
    title="Library Management API",
    version="1.0.0",
    description="📚 REST API для системы управления библиотекой книг",
    docs_url="/docs",  # URL для Swagger UI
    redoc_url="/redoc",  # URL для ReDoc
)

app.openapi = custom_openapi

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["health"])
async def health_check():
    """
    Проверка статуса API
    
    Возвращает текущий статус работы API системы управления библиотекой.
    """
    return {"status": "healthy", "message": "API is running successfully"}

# Book endpoints
@app.get("/books", response_model=List[BookResponse], tags=["books"])
async def read_books(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    Получить список всех книг
    
    - **skip**: Количество записей для пропуска (пагинация)
    - **limit**: Максимальное количество записей для возврата (пагинация)
    
    Возвращает список книг с поддержкой пагинации.
    """
    return get_books(db, skip=skip, limit=limit)

@app.get("/books/{book_id}", response_model=BookResponse, tags=["books"])
async def read_book(book_id: int, db: Session = Depends(get_db)):
    """
    Получить информацию о конкретной книге
    
    - **book_id**: ID книги (целое число)
    
    Возвращает полную информацию о книге по её ID.
    """
    db_book = get_book(db, book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book

@app.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED, tags=["books"])
async def add_book(book: BookCreate, db: Session = Depends(get_db)):
    """
    Добавить новую книгу
    
    Создает новую запись книги в библиотеке.
    
    **Обязательные поля:**
    - title: Название книги
    - author_id: ID автора
    
    **Опциональные поля:**
    - description: Описание книги
    - year: Год издания
    - isbn: ISBN номер
    """
    return create_book(db, book)

@app.put("/books/{book_id}", response_model=BookResponse, tags=["books"])
async def update_book_info(
    book_id: int, 
    book: BookUpdate, 
    db: Session = Depends(get_db)
):
    """
    Обновить информацию о книге
    
    - **book_id**: ID книги для обновления
    - **book**: Данные для обновления (только изменяемые поля)
    
    Обновляет информацию о существующей книге. Можно передавать только те поля, которые нужно изменить.
    """
    db_book = update_book(db, book_id, book)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book

@app.delete("/books/{book_id}", tags=["books"])
async def remove_book(book_id: int, db: Session = Depends(get_db)):
    """
    Удалить книгу
    
    - **book_id**: ID книги для удаления
    
    Удаляет книгу из библиотеки по указанному ID.
    """
    success = delete_book(db, book_id)
    if not success:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Book deleted successfully"}

# Author endpoints
@app.get("/authors", response_model=List[AuthorResponse], tags=["authors"])
async def read_authors(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    Получить список авторов
    
    - **skip**: Количество записей для пропуска (пагинация)
    - **limit**: Максимальное количество записей для возврата (пагинация)
    
    Возвращает список авторов с поддержкой пагинации.
    """
    return get_authors(db, skip=skip, limit=limit)

@app.get("/authors/{author_id}/books", response_model=List[BookResponse], tags=["authors"])
async def read_author_books(author_id: int, db: Session = Depends(get_db)):
    """
    Получить книги конкретного автора
    
    - **author_id**: ID автора
    
    Возвращает список всех книг, написанных указанным автором.
    """
    books = get_author_books(db, author_id)
    if not books:
        raise HTTPException(
            status_code=404, 
            detail="Author not found or no books for this author"
        )
    return books

@app.post("/authors", response_model=AuthorResponse, status_code=status.HTTP_201_CREATED, tags=["authors"])
async def add_author(author: AuthorCreate, db: Session = Depends(get_db)):
    """
    Добавить нового автора
    
    Создает новую запись автора в системе.
    
    **Обязательные поля:**
    - name: Имя автора
    
    **Опциональные поля:**
    - bio: Биография автора
    - birth_date: Дата рождения
    """
    return create_author(db, author)

# Search endpoint
@app.get("/books/search/{title}", response_model=List[BookResponse], tags=["search"])
async def search_books(title: str, db: Session = Depends(get_db)):
    """
    Поиск книг по названию
    
    - **title**: Фрагмент названия книги для поиска
    
    Возвращает список книг, в названии которых содержится указанный фрагмент.
    Поиск не чувствителен к регистру.
    
    **Пример:** поиск "война" найдет "Война и мир", "Война миров" и т.д.
    """
    books = search_books_by_title(db, title)
    if not books:
        raise HTTPException(
            status_code=404, 
            detail=f"No books found with title containing '{title}'"
        )
    return books
