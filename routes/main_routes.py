from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from models.user_model import User, db
from models.user_media_model import UserMedia
from models.diary_model import DiaryEntry
from models.book_model import Book
from models.cinema_model import Cinema
from models.music_model import Music
from sqlalchemy import desc
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from forms.forms import LoginForm, RegistrationForm, SearchForm

main_routes = Blueprint('main_routes', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@main_routes.route('/')
@login_required
def home():
    # Get user's most recent media for each type
    recent_books = UserMedia.query.filter_by(user_id=current_user.user_id, media_type='book')\
        .order_by(desc(UserMedia.created_at)).limit(1).first()
    
    recent_cinema = UserMedia.query.filter_by(user_id=current_user.user_id, media_type='cinema')\
        .order_by(desc(UserMedia.created_at)).limit(1).first()
    
    recent_music = UserMedia.query.filter_by(user_id=current_user.user_id, media_type='music')\
        .order_by(desc(UserMedia.created_at)).limit(1).first()
    
    # Combine into a list, filtering out None values
    recent_media = [item for item in [recent_books, recent_cinema, recent_music] if item is not None]
    
    return render_template('home.html', 
                         recent_media=recent_media)

@main_routes.route('/profile/<username>')
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    
    # Get user's recent activity
    recent_activity = UserMedia.query.filter_by(user_id=user.user_id)\
        .order_by(desc(UserMedia.created_at)).limit(5).all()
    
    # Get user's diary entries
    diary_entries = UserMedia.query.filter_by(user_id=user.user_id)\
        .order_by(desc(UserMedia.created_at)).limit(3).all()
    
    # Get followers and following counts
    followers_count = user.followers.count()
    following_count = user.following.count()
    
    return render_template('profile.html',
                         user=user,
                         recent_activity=recent_activity,
                         diary_entries=diary_entries,
                         followers_count=followers_count,
                         following_count=following_count)

@main_routes.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        # Handle basic information
        current_user.username = request.form.get('username')
        current_user.email = request.form.get('email')
        current_user.bio = request.form.get('bio')
        
        # Handle password change
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        if new_password:
            if new_password == confirm_password:
                from flask_bcrypt import Bcrypt
                bcrypt = Bcrypt()
                current_user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
            else:
                flash('Passwords do not match!', 'error')
                return redirect(url_for('main_routes.settings'))
        
        # Handle profile picture upload
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename != '':
                if allowed_file(file.filename):
                    # Create profile_pictures directory if it doesn't exist
                    profile_pictures_dir = os.path.join(current_app.root_path, 'static', 'profile_pictures')
                    os.makedirs(profile_pictures_dir, exist_ok=True)
                    
                    # Remove old profile picture if it exists and is not the default
                    if current_user.profile_picture and current_user.profile_picture != 'defaults/user.png':
                        old_path = os.path.join(current_app.root_path, 'static', current_user.profile_picture)
                        if os.path.exists(old_path):
                            os.remove(old_path)
                    
                    # Save new profile picture with secure filename
                    filename = secure_filename(file.filename)
                    # Add timestamp to avoid filename conflicts
                    name, ext = os.path.splitext(filename)
                    filename = f"{name}_{int(datetime.now().timestamp())}{ext}"
                    
                    file_path = os.path.join(profile_pictures_dir, filename)
                    file.save(file_path)
                    current_user.profile_picture = f'profile_pictures/{filename}'
                else:
                    flash('Invalid file type. Please upload an image file (png, jpg, jpeg, gif).', 'error')
                    return redirect(url_for('main_routes.settings'))
        
        # Handle profile picture deletion
        if request.form.get('delete_picture'):
            if current_user.profile_picture and current_user.profile_picture != 'defaults/user.png':
                old_path = os.path.join(current_app.root_path, 'static', current_user.profile_picture)
                if os.path.exists(old_path):
                    os.remove(old_path)
                current_user.profile_picture = 'defaults/user.png'
        
        # Handle notification settings
        current_user.email_notifications = 'email_notifications' in request.form
        current_user.notifications_enabled = 'activity_notifications' in request.form
        
        db.session.commit()
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('main_routes.settings'))
    
    return render_template('settings.html')

@main_routes.route('/stats')
@login_required
def stats():
    # Get user's media consumption statistics
    total_books = UserMedia.query.filter_by(user_id=current_user.user_id, media_type='book').count()
    total_movies = UserMedia.query.filter_by(user_id=current_user.user_id, media_type='cinema').count()
    total_music = UserMedia.query.filter_by(user_id=current_user.user_id, media_type='music').count()
    
    # Get genre distribution
    book_genres = db.session.query(Book.genre, db.func.count(UserMedia.user_media_id))\
        .join(UserMedia, Book.book_id == UserMedia.book_id)\
        .filter(UserMedia.user_id == current_user.user_id)\
        .group_by(Book.genre).all()
    
    movie_genres = db.session.query(Cinema.genre, db.func.count(UserMedia.user_media_id))\
        .join(UserMedia, Cinema.cinema_id == UserMedia.cinema_id)\
        .filter(UserMedia.user_id == current_user.user_id)\
        .group_by(Cinema.genre).all()
    
    # Get monthly activity
    monthly_activity = db.session.query(
        db.func.strftime('%Y-%m', UserMedia.created_at).label('month'),
        db.func.count(UserMedia.user_media_id).label('count')
    ).filter(
        UserMedia.user_id == current_user.user_id
    ).group_by('month').order_by('month').all()
    
    return render_template('stats.html',
                         total_books=total_books,
                         total_movies=total_movies,
                         total_music=total_music,
                         book_genres=book_genres,
                         movie_genres=movie_genres,
                         monthly_activity=monthly_activity)

@main_routes.route('/planner')
@login_required
def planner():
    # Get user's planned media
    planned_media = UserMedia.query.filter_by(
        user_id=current_user.id,
        status='planned'
    ).order_by(UserMedia.planned_date).all()
    
    return render_template('planner.html', planned_media=planned_media)

@main_routes.route('/network')
@login_required
def network():
    # Get followers and following as User lists
    followers_query = current_user.followers
    following_query = current_user.following
    followers = [f.follower for f in followers_query.all()]
    following = [f.followed for f in following_query.all()]
    followers_count = followers_query.count()
    following_count = following_query.count()
    
    # Get search results if any
    search_results = None
    if request.args.get('query'):
        search_results = User.query.filter(
            User.username.ilike(f"%{request.args.get('query')}%")
        ).all()
    
    return render_template('network.html',
                         followers=followers,
                         following=following,
                         followers_count=followers_count,
                         following_count=following_count,
                         search_results=search_results)

@main_routes.route('/media/<int:media_id>')
@login_required
def media_details(media_id):
    # Get the media item
    media = UserMedia.query.get_or_404(media_id)
    
    # Get network activity
    planned_by = User.query.join(UserMedia, User.user_id == UserMedia.user_id)\
        .filter(UserMedia.media_id == media_id, UserMedia.status == 'planned')\
        .all()
    
    consumed_by = User.query.join(UserMedia, User.user_id == UserMedia.user_id)\
        .filter(UserMedia.media_id == media_id, UserMedia.status == 'consumed')\
        .all()
    
    # Get diary entries if user has consumed this media
    diary_entries = []
    if media in current_user.consumed_media:
        diary_entries = DiaryEntry.query.filter_by(
            user_id=current_user.user_id,
            media_id=media_id
        ).order_by(DiaryEntry.created_at.desc()).all()
    
    return render_template('media.html',
                         media=media,
                         planned_by=planned_by,
                         consumed_by=consumed_by,
                         diary_entries=diary_entries)

@main_routes.route('/diary')
@login_required
def diary():
    """Diary page - now uses API for data loading"""
    return render_template('diary.html') 