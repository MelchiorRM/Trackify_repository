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
        # Handle settings update
        current_user.email = request.form.get('email')
        current_user.bio = request.form.get('bio')
        
        if request.form.get('new_password'):
            current_user.set_password(request.form.get('new_password'))
        
        # Handle profile picture upload
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename:
                # Save the file and update the profile picture path
                filename = secure_filename(file.filename)
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                current_user.profile_picture = filename
        
        # Handle notification settings
        current_user.email_notifications = 'email_notifications' in request.form
        current_user.activity_notifications = 'activity_notifications' in request.form
        
        # Handle privacy settings
        current_user.private_profile = 'private_profile' in request.form
        current_user.show_activity = 'show_activity' in request.form
        
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
    # Get followers and following
    followers = current_user.followers
    following = current_user.following
    
    # Get search results if any
    search_results = None
    if request.args.get('query'):
        search_results = User.query.filter(
            User.username.ilike(f"%{request.args.get('query')}%")
        ).all()
    
    return render_template('network.html',
                         followers=followers,
                         following=following,
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