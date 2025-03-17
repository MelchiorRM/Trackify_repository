from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models.user_model import User, db
from models.social_model import Follow, Like, Comment, Notification
from models.book_model import Book
from models.music_model import Music
from models.cinema_model import Cinema
from models.user_media_model import UserMedia
from flask_bcrypt import Bcrypt
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
    if not current_user.is_authenticated:
        return redirect(url_for("user_routes.login"))
    followed_id = [f.followed_id for f in Follow.query.filter_by(follower_id=current_user.user_id).all()]
    followed_id.append(current_user.user_id)
    user_media_entries = UserMedia.query.filter(UserMedia.user_id.in_(followed_id))\
                              .order_by(UserMedia.date_consumed.desc())\
                              .limit(50).all()
    media_items = []
    for entry in user_media_entries:
        item = (db.session.get(Book, entry.book_id) if entry.book_id else
                db.session.get(Music, entry.music_id) if entry.music_id else
                db.session.get(Cinema, entry.cinema_id)
                )
        if not item:
            continue
        user = db.session.get(User,entry.user_id)
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
    return render_template("dashboard.html", user=current_user, media_items=media_items)

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
                profile_picture_path = os.path.join('static/profile_pictures', profile_picture.filename)
                profile_picture.save(profile_picture_path)
                current_user.profile_picture = profile_picture_path
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