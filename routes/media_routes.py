from flask import Blueprint, request, render_template, session, redirect, url_for, flash
from flask_login import login_required, current_user
from models.book_model import Book, db
from models.music_model import Music
from models.cinema_model import Cinema
from models.books import search_books, save_books
from models.user_media_model import UserMedia

media_routes = Blueprint('media_routes', __name__)
@media_routes.route("/books", methods=["GET", "POST"])
@login_required
def books():
    books = []
    search_query = request.args.get('search_query','')
    page = int(request.args.get('page', 1))
    if request.method == "POST":
        search_query = request.form.get("search_query")
        if search_query:
            return redirect(url_for('media_routes.books', search_query=search_query, page=1))
        else:
            book_data = {
                "title": request.form["title"],
                "author": request.form["author"],
                "genre": request.form["genre"],
                "year": request.form["year"],
                "language": request.form["language"],
                "publisher": request.form["publisher"],
                "country": request.form["country"],
                "rating": request.form["rating"],
                "reviews": request.form["reviews"],
                "coverart": request.form["coverart"],
            }
            user_id = current_user.user_id
            save_books(book_data, user_id)
            flash("Book added to library!", "success")
            return redirect(url_for("media_routes.books"))
    if search_query:
        books, total_results, current_page = search_books(search_query, page)
        results_per_page = 20
        start_index = (current_page - 1) * results_per_page
        end_index = start_index + results_per_page
        paged_books = books[start_index:end_index]
        has_next = end_index < total_results
        has_prev = current_page > 1
    else:
        user_media_entries = UserMedia.query.filter_by(user_id=current_user.user_id, media_type='book').all()
        paged_books = [Book.query.get(entry.book_id) for entry in user_media_entries if entry.book_id]
        has_next = False
        has_prev = False
        current_page = 1
    return render_template("book.html", books=paged_books, search_query=search_query, page=current_page, has_next=has_next, has_prev=has_prev)

@media_routes.route("/music", methods=["GET", "POST"])
@login_required
def music():
    if request.method == "POST":
        title = request.form["title"]
        artist = request.form["artist"]
        genre = request.form["genre"]
        year = request.form["year"]
        language = request.form["language"]
        label = request.form ["label"]
        country = request.form["country"]
        rating = request.form["rating"]
        reviews = request.form["reviews"]
        coverart = request.form["coverart"]
        music = Music(title, artist, genre, year, language, label, country, rating, reviews, coverart)
        db.session.add(music)
        db.session.commit()
        return redirect(url_for("media_routes.music"))
    music = Music.query.all()
    return render_template("music.html", music=music)

@media_routes.route("/cinema", methods = ["GET", "POST"])
@login_required
def cinema():
    if request.method == "POST":
        title = request.form["title"]
        genre = request.form["genre"]
        year = request.form["year"]
        country = request.form["country"]
        director = request.form["director"]
        type = request.form["type"]
        language = request.form["language"]
        rating = request.form["rating"]
        reviews = request.form["reviews"]
        coverart = request.form["coverart"]
        cinema = Cinema(title, genre, year, country, director, type, language, rating, reviews, coverart)
        db.session.add(cinema)
        db.session.commit()
        return redirect(url_for("media_routes.cinema"))
    cinema = Cinema.query.all()
    return render_template("cinema.html", cinema=cinema)

@media_routes.route("/library")
@login_required
def library():
    user_id = current_user.user_id
    user_media_entries = UserMedia.query.filter_by(user_id=user_id).all()
    books = []
    music = []
    cinema = []

    for entry in user_media_entries:
        if entry.media_type == "book":
            book = Book.query.get(entry.book_id)
            books.append(book)
        elif entry.media_type == "music":
            music.append(Music.query.get(entry.music_id))
        elif entry.media_type == "cinema":
            cinema.append(Cinema.query.get(entry.cinema_id))
    return render_template("library.html", books=books, music=music, cinema=cinema)