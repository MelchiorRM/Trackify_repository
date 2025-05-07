import requests
from models.book_model import Book, db
from models.user_media_model import UserMedia
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
            "rating": float(volume_info.get("averageRating")) if volume_info.get("averageRating") else None,
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
            "rating": None,
            "reviews": doc.get("description", "No Description Available"),
            "coverart": f"https://covers.openlibrary.org/b/id/{doc.get('cover_i', '')}-L.jpg" if doc.get("cover_i") else None,
        }
        books.append(book_data)
    return books, data.get("numFound", 0), page

def save_books(book_data, user_id, review=None, rating=None, date_consumed=None):
    from utils.completion import enrich_single_media_item
    existing_book = Book.query.filter_by(title=book_data["title"], author=book_data["author"]).first()
    if not existing_book:
        book = Book(
            title=book_data["title"],
            author=book_data["author"],
            genre=book_data.get("genre", "Unknown"),
            year=book_data.get("year"),
            language=book_data.get("language"),
            publisher=book_data.get("publisher"),
            country=book_data.get("country"),
            description=book_data.get("reviews"),  # Use reviews as description
            coverart=book_data.get("coverart")
        )
        db.session.add(book)
        db.session.flush() # flush to get the book_id
        # Enrich the book data before commit
        enrich_single_media_item(book, "book")
    else:
        book = existing_book

    user_media_entry = UserMedia.query.filter_by(user_id=user_id, media_type='book',book_id=book.book_id).first()
    if not user_media_entry:
        user_media_entry = UserMedia(
            user_id=user_id,
            book_id=book.book_id,
            media_type='book',
            review=review,
            rating=float(rating) if rating and rating != 'None' else None,
            date_consumed=date_consumed if date_consumed and date_consumed != '' else None,
            done=True if date_consumed and date_consumed != '' else False
            )
    else:
        if review:
            user_media_entry.review = review
        if rating and rating != 'None':
            user_media_entry.rating = float(rating)
        if date_consumed and date_consumed != '':
            user_media_entry.date_consumed = date_consumed
            user_media_entry.done = True
        db.session.add(user_media_entry)
    db.session.commit()
    return book
