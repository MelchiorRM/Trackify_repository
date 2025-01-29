from flask import Blueprint, request, render_template, session, redirect, url_for, flash
from flask_login import login_required, current_user
from models.book_model import Book, db
from models.music_model import Music
from models.cinema_model import Cinema
from models.books import search_books, save_books
from models.cinema import search_cinema, save_cinema
from models.music import search_music, save_music
from models.user_media_model import UserMedia

media_routes = Blueprint('media_routes', __name__)

@media_routes.route("/search", methods=["GET"])
@login_required
def search():
    search_query = request.args.get('search_query')
    media_type = request.args.get('media_type')
    if media_type == "books":
        return redirect(url_for('media_routes.books', search_query=search_query, page=1))
    elif media_type == "music":
        return redirect(url_for('media_routes.music', search_query=search_query, page=1))
    elif media_type == "cinema":
        return redirect(url_for('media_routes.cinema', search_query=search_query, page=1))
    else:
        flash("Invalid media type", "danger")
        return redirect(url_for('user_routes.dashboard'))

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
    music = []
    search_query = request.args.get('search_query', '')
    page = int(request.args.get('page', 1))
    if request.method == "POST":
        search_query = request.form.get("search_query")
        if search_query:
            return redirect(url_for("media_routes.music", search_query=search_query, page=page))
        else:
            music_data = {
                "title": request.form.get("title"),
                "artist": request.form.get("artist"),
                "genre": request.form.get("genre"),
                "year": request.form.get("year"),
                "language": request.form.get("language"),
                "label": request.form.get("label"),
                "country": request.form.get("country"),
                "rating": request.form.get("rating"),
                "reviews": request.form.get("reviews"),
                "coverart": request.form.get("coverart")
            }
            user_id = current_user.user_id
            save_music(music_data, user_id)
            flash("Music added to library!", "success")
            return redirect(url_for("media_routes.music"))
    if search_query:
        music, total_results, current_page = search_music(search_query, page)
        results_per_page = 20
        start_index = (current_page - 1) * results_per_page
        end_index = start_index + results_per_page
        paged_music = music[start_index:end_index]
        has_next = end_index < total_results
        has_prev = current_page > 1
    else:
        user_media_entries = UserMedia.query.filter_by(user_id=current_user.user_id, media_type='music').all()
        paged_music = [Music.query.get(entry.music_id) for entry in user_media_entries if entry.music_id]
        has_next = False
        has_prev = False
        current_page = 1
    return render_template("music.html", search_query=search_query, music=paged_music, page=current_page, has_next=has_next, has_prev=has_prev)

@media_routes.route("/cinema", methods = ["GET", "POST"])
@login_required
def cinema():
    cinema = []
    search_query = request.args.get('search_query', '')
    page = int(request.args.get('page', 1))
    if request.method == "POST":
        search_query = request.form.get("search_query")
        if search_query:
            return redirect(url_for("media_routes.cinema", search_query=search_query, page=page))
        else:
            cinema_data = {
                "title": request.form.get("title"),
                "genre": request.form.get("genre"),
                "year": request.form.get("year"),
                "country": request.form.get("country"),
                "director": request.form.get("director"),
                "type": request.form.get("type", ""), 
                "language": request.form.get("language"),
                "rating": request.form.get("rating"),
                "reviews": request.form.get("reviews"),
                "coverart": request.form.get("coverart")
            }
            user_id = current_user.user_id
            save_cinema(cinema_data, user_id)
            flash("Cinema added to library!", "success")
            return redirect(url_for("media_routes.cinema"))
    if search_query:
        cinema, total_results, current_page = search_cinema(search_query, page)
        results_per_page = 20
        start_index = (current_page - 1) * results_per_page
        end_index = start_index + results_per_page
        paged_cinema = cinema[start_index:end_index]
        has_next = end_index < total_results
        has_prev = current_page > 1
    else:
        user_media_entries = UserMedia.query.filter_by(user_id=current_user.user_id, media_type='cinema').all()
        paged_cinema = [Cinema.query.get(entry.cinema_id) for entry in user_media_entries if entry.cinema_id]
        has_next = False
        has_prev = False
        current_page = 1
    return render_template("cinema.html", cinema=paged_cinema, search_query=search_query, page=current_page, has_next=has_next, has_prev=has_prev)

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