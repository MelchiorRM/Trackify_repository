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
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from forms.forms import LoginForm, RegistrationForm, SearchForm, ProfileForm, RequestPasswordResetForm, ResetPasswordForm
from datetime import datetime
from utils.email_utils import send_password_reset_email, send_password_changed_email

user_routes = Blueprint('user_routes', __name__)
bcrypt = Bcrypt()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@user_routes.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main_routes.home'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists', 'error')
            return render_template('register.html', form=form)
        
        user = User(
            username=form.username.data,
            password=form.password.data,
            email=form.email.data
        )
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        flash('Registration successful!', 'success')
        return redirect(url_for('main_routes.home'))
    return render_template('register.html', form=form)

@user_routes.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main_routes.home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main_routes.home'))
        flash('Invalid username or password', 'error')
    return render_template('login.html', form=form)

@user_routes.route("/logout")
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main_routes.home'))

@user_routes.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        current_user.username = request.form["username"]
        current_user.email = request.form["email"]
        password = request.form["password"]
        if password:
            current_user.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Handle profile picture upload
        if 'profile_picture' in request.files:
            profile_picture = request.files['profile_picture']
            if profile_picture and profile_picture.filename != '':
                if allowed_file(profile_picture.filename):
                    # Create profile_pictures directory if it doesn't exist
                    profile_pictures_dir = os.path.join(current_app.root_path, 'static', 'profile_pictures')
                    os.makedirs(profile_pictures_dir, exist_ok=True)
                    
                    # Remove old profile picture if it exists and is not the default
                    if current_user.profile_picture and current_user.profile_picture != 'defaults/user.png':
                        old_path = os.path.join(current_app.root_path, 'static', current_user.profile_picture)
                        if os.path.exists(old_path):
                            os.remove(old_path)
                    
                    # Save new profile picture with secure filename
                    filename = secure_filename(profile_picture.filename)
                    # Add timestamp to avoid filename conflicts
                    name, ext = os.path.splitext(filename)
                    filename = f"{name}_{int(datetime.now().timestamp())}{ext}"
                    
                    profile_picture_path = os.path.join(profile_pictures_dir, filename)
                    profile_picture.save(profile_picture_path)
                    current_user.profile_picture = f'profile_pictures/{filename}'
                else:
                    flash('Invalid file type. Please upload an image file (png, jpg, jpeg, gif).', 'error')
                    return redirect(url_for("user_routes.profile"))

        # Handle profile picture deletion
        if request.form.get("delete_picture"):
            if current_user.profile_picture and current_user.profile_picture != 'defaults/user.png':
                old_path = os.path.join(current_app.root_path, 'static', current_user.profile_picture)
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
    query = request.form.get('query', '').strip()
    if not query:
        flash('Please enter a search term', 'error')
        return redirect(url_for('main_routes.home'))
    
    users = User.query.filter(User.username.ilike(f'%{query}%')).all()
    return render_template('search_users.html', users=users)

@user_routes.route("/follow/<username>", methods=["POST"])
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first_or_404()
    if user == current_user:
        flash('You cannot follow yourself!', 'error')
        return redirect(url_for('main_routes.profile', username=username))
    
    if current_user.is_following(user):
        current_user.unfollow(user)
        flash(f'You have unfollowed {username}.', 'info')
    else:
        current_user.follow(user)
        flash(f'You are now following {username}.', 'success')
    
    return redirect(url_for('main_routes.profile', username=username))

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
    from utils.recommendations import get_user_consumption, combine_and_randomize_recommendations
    focus = request.args.get("focus")
    type_filter = request.args.get("type_filter", "all")
    value_filter = request.args.get("value_filter")
    page = int(request.args.get("page", 1))

    user_consumption = get_user_consumption(current_user.user_id, db.session)
    consumed_books = user_consumption["books"]
    consumed_movies = user_consumption["movies"]
    consumed_music = user_consumption["music"]

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

    combined_data = combine_and_randomize_recommendations(current_user.user_id, consumed_books, consumed_movies, consumed_music, page=page)

    combined_recommendations = combined_data["recommendations"]

    # Apply type_filter to combined list
    if type_filter != "all":
        combined_recommendations = [rec for rec in combined_recommendations if rec["type"] == type_filter]

    return render_template(
        "recommendations.html",
        recommendations=combined_recommendations,
        focus=focus,
        type_filter=type_filter,
        value_filter=value_filter,
        current_page=combined_data.get("current_page", 1),
        total_pages=combined_data.get("total_pages", 1)
    )

@user_routes.route("/request_password_reset", methods=["GET", "POST"])
def request_password_reset():
    if current_user.is_authenticated:
        return redirect(url_for('main_routes.home'))
    
    form = RequestPasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            # Generate reset token
            token = user.generate_reset_token()
            db.session.commit()
            
            # Create reset URL
            reset_url = url_for('user_routes.reset_password', token=token, _external=True)
            
            # Send email
            if send_password_reset_email(user, reset_url):
                flash('Password reset instructions have been sent to your email.', 'success')
            else:
                flash('Failed to send password reset email. Please try again.', 'error')
            
            return redirect(url_for('user_routes.login'))
    
    return render_template('request_password_reset.html', form=form)

@user_routes.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main_routes.home'))
    
    # Find user by token
    user = User.query.filter_by(reset_token=token).first()
    
    if not user or not user.verify_reset_token(token):
        flash('Invalid or expired reset token.', 'error')
        return redirect(url_for('user_routes.request_password_reset'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        # Update password
        user.password_hash = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.clear_reset_token()
        db.session.commit()
        
        # Send confirmation email
        send_password_changed_email(user)
        
        flash('Your password has been reset successfully.', 'success')
        return redirect(url_for('user_routes.login'))
    
    return render_template('reset_password.html', form=form, token=token)

@user_routes.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.bio = form.bio.data
        
        # Handle profile picture upload
        if form.profile_picture.data:
            if allowed_file(form.profile_picture.data.filename):
                # Create profile_pictures directory if it doesn't exist
                profile_pictures_dir = os.path.join(current_app.root_path, 'static', 'profile_pictures')
                os.makedirs(profile_pictures_dir, exist_ok=True)
                
                # Remove old profile picture if it exists and is not the default
                if current_user.profile_picture and current_user.profile_picture != 'defaults/user.png':
                    old_path = os.path.join(current_app.root_path, 'static', current_user.profile_picture)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                # Save new profile picture with secure filename
                filename = secure_filename(form.profile_picture.data.filename)
                # Add timestamp to avoid filename conflicts
                name, ext = os.path.splitext(filename)
                filename = f"{name}_{int(datetime.now().timestamp())}{ext}"
                
                profile_picture_path = os.path.join(profile_pictures_dir, filename)
                form.profile_picture.data.save(profile_picture_path)
                current_user.profile_picture = f'profile_pictures/{filename}'
            else:
                flash('Invalid file type. Please upload an image file (png, jpg, jpeg, gif).', 'error')
                return render_template('edit_profile.html', form=form)
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('main_routes.profile', username=current_user.username))
    return render_template('edit_profile.html', form=form)
