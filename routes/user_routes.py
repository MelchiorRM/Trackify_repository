from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from models.user_model import User, db
from models.social_model import Follow, Like, Comment, Notification
from utils.pagination import paginate
from models.book_model import Book
from models.music_model import Music
from models.cinema_model import Cinema
from models.user_media_model import UserMedia
from flask_bcrypt import Bcrypt
from config import Config
import os

user_routes = Blueprint('user_routes', __name__)
bcrypt = Bcrypt()

@user_routes.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]
        profile_picture = request.files.get('profile_picture')
        if profile_picture and profile_picture.filename != '':
            profile_picture_path = os.path.join('static/profile_pictures', profile_picture.filename)
            profile_picture.save(profile_picture_path)
        else:
            profile_picture_path = 'defaults/user.png'
        if User.query.filter_by(username=username).first():
            flash("Username already exists!")
            return redirect(url_for("user_routes.register"))
        if User.query.filter_by(email=email).first():
            flash("Email already registered!")
            return redirect(url_for("user_routes.register"))
        user = User(username=username, password=password, email=email, profile_picture=profile_picture_path)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful! Please login", "success")
        return redirect(url_for("user_routes.login"))
    return render_template("register.html")

@user_routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("user_routes.dashboard"))
        else:
            flash("Invalid username or password", "danger")
            return redirect(url_for("user_routes.login"))
    return render_template("login.html")


@user_routes.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    page = int(request.args.get("page", 1))
    per_page = 10
    followed_id = [f.followed_id for f in Follow.query.filter_by(follower_id=current_user.user_id).all()]
    followed_id.append(current_user.user_id)
    query = UserMedia.query.filter(UserMedia.user_id.in_(followed_id)).order_by(UserMedia.date_consumed.desc())
    pagination = paginate(query, page, per_page)
    media_items = []
    for entry in pagination["items"]:
        item = (db.session.get(Book, entry.book_id) if entry.book_id else
                db.session.get(Music, entry.music_id) if entry.music_id else
                db.session.get(Cinema, entry.cinema_id))
        if not item:
            continue
        user = db.session.get(User, entry.user_id)
        likes = Like.query.filter_by(user_media_id=entry.user_media_id).count()
        comments = Comment.query.filter_by(user_media_id=entry.user_media_id).order_by(Comment.created_at.desc()).all()
        liked_by_me = Like.query.filter_by(user_id=current_user.user_id, user_media_id=entry.user_media_id).first()
        is_followed = Follow.query.filter_by(follower_id=current_user.user_id, followed_id=user.user_id).first()
        media_items.append({
            "item": item,
            "entry": entry,
            "user": user,
            "likes": likes,
            "comments": comments,
            "liked_by_me": bool(liked_by_me),
            "is_followed": bool(is_followed)
        })
    return render_template("dashboard.html", user=current_user, media_items=media_items, pagination=pagination)

@user_routes.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("user_routes.login"))

@user_routes.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        current_user.username = request.form["username"]
        current_user.email = request.form["email"]
        password = request.form["password"]
        if password:
            current_user.password = password
        if 'profile_picture' in request.files:
            profile_picture = request.files['profile_picture']
            if profile_picture and profile_picture.filename != '':
                if current_user.profile_picture != 'defaults/user.png':
                    old_path = os.path.join('static', current_user.profile_picture)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                profile_picture_path = os.path.join('static/profile_pictures', profile_picture.filename)
                profile_picture.save(profile_picture_path)
                current_user.profile_picture = profile_picture_path
        if request.form.get("delete_picture"):
            if current_user.profile_picture != 'defaults/user.png':
                old_path = os.path.join('static', current_user.profile_picture)
                if os.path.exists(old_path):
                    os.remove(old_path)
                current_user.profile_picture = 'defaults/user.png'
        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("user_routes.profile"))
    return render_template("profile.html", user=current_user)

@user_routes.route("/search_users", methods=["GET", "POST"])
@login_required
def search_users():
    search_query = request.form.get("query") if request.method == "POST" else request.args.get("query")
    
    if not search_query:
        flash("Please enter a search query.", "danger")
        return redirect(url_for("user_routes.dashboard"))
    users = User.query.filter(User.username.ilike(f"%{search_query}%")).all()
    
    print("users found", users)
    for user in users:
        print(users)
        
    results = []
    for user in users:
        if user.user_id == current_user.user_id:
            continue
        is_followed = Follow.query.filter_by(follower_id=current_user.user_id, followed_id=user.user_id).first()
        results.append({
            "user": user,
            "is_followed": bool(is_followed)
        })
    return render_template("search_users.html", results=results, search_query=search_query)
@user_routes.route("/follow/<int:user_id>", methods=["POST"])
@login_required
def follow(user_id):
    if user_id == current_user.user_id:
        flash("You cannot follow yourself", "danger")
        return redirect(request.referrer)
    existing_follow = Follow.query.filter_by(follower_id=current_user.user_id, followed_id=user_id).first()
    if existing_follow:
        flash("You are already following this user", "info")
        return redirect(request.referrer)
    follow = Follow(follower_id=current_user.user_id, followed_id=user_id)
    db.session.add(follow)
    db.session.commit()
    flash(f"You are now following {User.query.get(user_id).username}", "success")
    return redirect(request.referrer)

@user_routes.route("/unfollow/<int:user_id>", methods=["POST"])
@login_required
def unfollow(user_id):
    follow = Follow.query.filter_by(follower_id=current_user.user_id, followed_id=user_id).first()
    if follow:
        db.session.delete(follow)
        db.session.commit()
        flash(f"You are no longer following {user_id.username}", "success")
    return redirect(request.referrer)

@user_routes.route("/like/<int:user_media_id>", methods=["POST"])
@login_required
def like(user_media_id):
    like = Like(user_id=current_user.user_id, user_media_id=user_media_id)
    db.session.add(like)
    db.session.commit()
    flash("Liked!", "success")
    return redirect(request.referrer)


@user_routes.route("/unlike/<int:user_media_id>", methods=["POST"])
@login_required
def unlike(user_media_id):
    like = Like.query.filter_by(user_id=current_user.user_id, user_media_id=user_media_id).first()
    if like:
        db.session.delete(like)
        db.session.commit()
        flash("Unliked!", "success")
    return redirect(request.referrer)

@user_routes.route("/comment/<int:user_media_id>", methods=["GET","POST"])
@login_required
def comment(user_media_id):
    content = request.form["content"]
    if not content:
        flash("Comment cannot be empty", "danger")
        return redirect(request.referrer)
    comment = Comment(user_id=current_user.user_id, user_media_id=user_media_id, content=content)
    db.session.add(comment)
    db.session.commit()
    flash("Comment added!", "success")
    return redirect(request.referrer)

@user_routes.route("/notifications", methods=["GET"])
@login_required
def notifications():
    notifications = Notification.query.filter_by(user_id=current_user.user_id).order_by(Notification.created_at.desc()).all()
    return render_template("notifications.html", notifications=notifications)

@user_routes.route("/recommendations", methods=["GET"])
@login_required
def recommendations():
    import google.generativeai as genai
    import json, requests
    from sqlalchemy import or_

    focus = request.args.get("focus")
    type_filter = request.args.get("type_filter")
    value_filter = request.args.get("value_filter")

    def get_user_consumption():
        return {
            "books": Book.query.join(UserMedia, Book.book_id == UserMedia.book_id).filter(UserMedia.user_id == current_user.user_id).all(),
            "movies": Cinema.query.join(UserMedia, Cinema.cinema_id == UserMedia.cinema_id).filter(UserMedia.user_id == current_user.user_id).all(),
            "music": Music.query.join(UserMedia, Music.music_id == UserMedia.music_id).filter(UserMedia.user_id == current_user.user_id).all(),
        }
    def recommend(consumed_books, consumed_movies, consumed_music):
        authors = [b.author for b in consumed_books]
        book_genres = [b.genre for b in consumed_books]
        directors = [m.director for m in consumed_movies]
        movie_genres = [m.genre for m in consumed_movies]
        artists = [m.artist for m in consumed_music]
        music_genres = [m.genre for m in consumed_music]

        print(f"Authors for recommendation: {authors}")
        print(f"Book genres for recommendation: {book_genres}")
        print(f"Directors for recommendation: {directors}")
        print(f"Movie genres for recommendation: {movie_genres}")
        print(f"Artists for recommendation: {artists}")
        print(f"Music genres for recommendation: {music_genres}")

        recom_books = Book.query.filter(
            or_(
                Book.author.in_(authors),
                *[Book.genre.like(f"%{genre.strip()}%") for genre in book_genres if genre and genre != "Unknown"]
            )
            # Removed negation filter to test recommendations
            # ~Book.book_id.in_([b.book_id for b in consumed_books])  # Use the correct primary key field
        ).limit(10).all()

        recom_movies = Cinema.query.filter(
            or_(
                Cinema.director.in_(directors),
                *[Cinema.genre.like(f"%{genre.strip()}%") for genre in movie_genres if genre]
            )
            # Removed negation filter to test recommendations
            # ~Cinema.cinema_id.in_([m.cinema_id for m in consumed_movies])  # Use the correct primary key field
        ).limit(10).all()

        recom_music = Music.query.filter(
            or_(
                *[Music.artist.like(f"%{artist.strip()}%") for artist in artists if artist],
                *[Music.genre.like(f"%{genre.strip()}%") for genre in music_genres if genre and genre != "Unknown"]
            )
            # Removed negation filter to test recommendations
            # ~Music.music_id.in_([m.music_id for m in consumed_music])  # Use the correct primary key field
        ).limit(10).all()

        return recom_books, recom_movies, recom_music


    def collaborative_filtering(consumed_books, consumed_movies, consumed_music):
        similar_users = [
            f.followed_id for f in Follow.query.filter_by(follower_id=current_user.user_id).all()
        ]

        print(f"Similar users for collaborative filtering: {similar_users}")

        commun_books = Book.query.join(UserMedia, Book.book_id == UserMedia.book_id).filter(
            UserMedia.user_id.in_(similar_users)
            # Removed negation filter to test recommendations
            # ~UserMedia.book_id.in_([b.book_id for b in consumed_books])  # Use the correct primary key field
        ).limit(5).all()

        commun_movies = Cinema.query.join(UserMedia, Cinema.cinema_id == UserMedia.cinema_id).filter(
            UserMedia.user_id.in_(similar_users)
            # Removed negation filter to test recommendations
            # ~UserMedia.cinema_id.in_([m.cinema_id for m in consumed_movies])  # Use the correct primary key field
        ).limit(5).all()

        commun_music = Music.query.join(UserMedia, Music.music_id == UserMedia.music_id).filter(
            UserMedia.user_id.in_(similar_users)
            # Removed negation filter to test recommendations
            # ~UserMedia.music_id.in_([m.music_id for m in consumed_music])  # Use the correct primary key field
        ).limit(5).all()

        return commun_books, commun_movies, commun_music

    # Helper function to build GPT prompt
    def build_prompt(consumed_books, consumed_movies, consumed_music):
        format_items = "\n".join([
            f'- {type(item).__name__}: "{item.title}" by {getattr(item, "author", getattr(item, "director", getattr(item, "artist", "Unknown")))} (genre: {getattr(item, "genre", "Unknown")})'
            for item in consumed_books + consumed_movies + consumed_music
        ])
        return f"""
The user is interested in works like:
{format_items}
Recommend 5 culturally, thematically, or stylistically connected titles across books, music, or movies.
Only return valid known titles in JSON format:
[
{{"title": "Sample Title", "type": "book"}},
{{"title": "Sample Title", "type": "movie"}},
...,
{{"title": "Sample Title", "type": "music"}}
]
Only return the JSON array.
""".strip()

    # Helper function to call Gemini API
    def call_gemini_api(prompt):
        api_key = current_app.config.get('GEMINI_API_KEY')
        if not api_key:
            print("Error: GEMINI_API_KEY not configured.")
            return [] 

        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)  
            print(f"Gemini Raw Response Text (Recommendations): {response.text}")
            cleaned_text = response.text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[len("```json"):]
            elif cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[len("```"):]
            
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-len("```")]
            
            cleaned_text = cleaned_text.strip()
            if not cleaned_text:
                print("Error: Gemini returned an empty response after cleaning.")
                return []
            gemini_recom = json.loads(cleaned_text)
            if isinstance(gemini_recom, list):
                return gemini_recom
            else:
                print(f"Error: Gemini response was not a JSON list as expected. Got: {type(gemini_recom)}")
                return []
        except json.JSONDecodeError as e:
            print("Gemini API error:", e)
            return []

    # Debug prints to check data
    user_consumption = get_user_consumption()
    consumed_books = user_consumption["books"]
    consumed_movies = user_consumption["movies"]
    consumed_music = user_consumption["music"]

    print(f"Consumed books count: {len(consumed_books)}")
    print(f"Consumed movies count: {len(consumed_movies)}")
    print(f"Consumed music count: {len(consumed_music)}")

    # Apply focus and filtering
    if focus and value_filter:
        if focus == "genre":
            consumed_books = [b for b in consumed_books if b.genre == value_filter]
            consumed_movies = [m for m in consumed_movies if m.genre == value_filter]
            consumed_music = [m for m in consumed_music if m.genre == value_filter]
        elif focus == "author":
            consumed_books = [b for b in consumed_books if b.author == value_filter]
        elif focus == "director":
            consumed_movies = [m for m in consumed_movies if m.director == value_filter]
        elif focus == "artist":
            consumed_music = [m for m in consumed_music if m.artist == value_filter]

    _books, _movies, _music = recommend(consumed_books, consumed_movies, consumed_music)
    commun_books, commun_movies, commun_music = collaborative_filtering(consumed_books, consumed_movies, consumed_music)

    print(f"Recommended books count: {len(_books)}")
    print(f"Recommended movies count: {len(_movies)}")
    print(f"Recommended music count: {len(_music)}")

    print(f"Collaborative books count: {len(commun_books)}")
    print(f"Collaborative movies count: {len(commun_movies)}")
    print(f"Collaborative music count: {len(commun_music)}")

    gemini_prompt = build_prompt(consumed_books, consumed_movies, consumed_music)
    gemini_recom = call_gemini_api(gemini_prompt)

    print(f"Gemini recommendations raw: {gemini_recom}")

    gemini_books, gemini_movies, gemini_music = [], [], []
    if isinstance(gemini_recom, list):
        for item in gemini_recom:
            if isinstance(item, dict) and "title" in item and "type" in item:
                title, mtype = item["title"], item["type"].lower()
                if mtype == "book":
                    gemini_books.append(Book.query.filter_by(title=title).first())
                elif mtype == "movie":
                    gemini_movies.append(Cinema.query.filter_by(title=title).first())
                elif mtype == "music":
                    gemini_music.append(Music.query.filter_by(title=title).first())
    else:
        print(f"Error: Gemini recommendations were not a list. Got: {type(gemini_recom)}")

    # Filter out None values from gemini lists
    gemini_books = [b for b in gemini_books if b is not None]
    gemini_movies = [m for m in gemini_movies if m is not None]
    gemini_music = [mu for mu in gemini_music if mu is not None]

    print(f"Gemini books count: {len(gemini_books)}")
    print(f"Gemini movies count: {len(gemini_movies)}")
    print(f"Gemini music count: {len(gemini_music)}")

    return render_template(
        "recommendations.html",
        books=_books,
        movies=_movies,
        music=_music,
        commun_books=commun_books,
        commun_movies=commun_movies,
        commun_music=commun_music,
        gemini_books=gemini_books,
        gemini_movies=gemini_movies,
        gemini_music=gemini_music,
        focus=focus,
        type_filter=type_filter,
        value_filter=value_filter
    )
