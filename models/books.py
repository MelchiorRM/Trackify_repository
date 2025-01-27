import requests
from models.book_model import Book, db
from flask import current_app

def search_books(query, page=1):
    local_books = []
    if query:
        local_books = Book.query.filter(Book.title.contains(query)).all()

    local_results = [{
        "title": book.title,
        "author": book.author,
        "genre": book.genre,
        "year": book.year,
        "language": book.language,
        "publisher": book.publisher,
        "country": book.country,
        "rating": book.rating,
        "reviews": book.reviews,
        "coverart": book.coverart
        } for book in local_books]
    
    google_books, google_total, _ = search_google_books(query)
    open_library_books , open_library_total, _ = search_open_library(query, page)
    results = local_results + google_books + open_library_books
    results_len = len(local_results) + google_total + open_library_total
    return results, results_len, page

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
    return books, data.get("totalItems", 0), 1

def search_open_library(query, page=1):
    url = f"https://openlibrary.org/search.json?q={query}&page={page}"
    response = requests.get(url)
    data = response.json()
    books = []
    for doc in data.get("docs", []):
        book_data = {
            "title": doc.get("title"),
            "author": ",".join(doc.get("author_name", [])),
            "genre": ",".join(doc.get("subject", [])),
            "year": doc.get("first_publish_year"),
            "country": doc.get("publish_country"),
            "rating": doc.get("ratings_average", "No Rating"),
            "reviews": doc.get("description", "No Description Available"),
            "coverart": f"https://covers.openlibrary.org/b/id/{doc.get('cover_i', '')}-L.jpg" if doc.get("cover_i") else None,
        }
        books.append(book_data)
    return books, data.get("numFound", 0), page

def save_books(book_data):
    existing_book = Book.query.filter_by(title=book_data["title"], author=book_data["author"]).first()
    if existing_book:
        return existing_book
    book = Book(**book_data)
    db.session.add(book)
    db.session.commit()
    return book