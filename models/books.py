import requests
from models.book_model import Book, db
from flask import current_app

def search_books(query):
    books = Book.query.filter(Book.title.contains(query)).all()
    if not books:
        books = search_google_books(query)
    return books

def search_google_books(query):
    api_key = current_app.config.get('GOOGLE_BOOKS_API_KEY')
    url = f'https://www.googleapis.com/books/v1/volumes?q={query}&key={api_key}'
    response = requests.get(url)
    data = response.json()
    books = []
    for item in data.get("items",[]):
        volume_info = item.get("volumeInfo")
        book_data = {
            "title": volume_info.get("title"),
            "author": ",".join(volume_info.get("authors",[])),
            "genre": ",".join(volume_info.get("categories",[])),
            "year": int(volume_info.get("publishedDate","0")[:4]) if volume_info.get("publishedDate") else 0,
            "country": volume_info.get("country"),
            "rating": volume_info.get("averageRating"),
            "reviews": volume_info.get("description"),
            "coverart": volume_info.get("imageLinks", {}).get("thumbnail"),
        }
        books.append(book_data)
    return books

def save_books(books):
    book = Book(**book)
    db.session.add(book)
    db.session.commit()
    return book