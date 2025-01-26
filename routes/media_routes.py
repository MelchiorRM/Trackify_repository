from flask import Blueprint, request, render_template, session, redirect, url_for
from flask_login import login_required
from models.book_model import Book, db
from models.music_model import Music
from models.cinema_model import Cinema
from models.books import search_books, save_books

media_routes = Blueprint('media_routes', __name__)
@media_routes.route("/books", methods=["GET", "POST"])
@login_required
def books():
    books = []
    search_query = None
    if request.method == "POST":
        search_query = request.form.get("search_query")
        if search_query:
            books = search_books(search_query)
            return render_template("book.html", books=books, search_query=search_query)
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
            book = save_books(book_data)
            return redirect(url_for("media_routes.books"))
    books = Book.query.all()
    return render_template("book.html", books=books)

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