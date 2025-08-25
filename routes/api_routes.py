from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models.user_media_model import UserMedia
from models.user_model import db, User
from models.social_model import List, ListItem, Follow, Notification
from models.books import Book
from models.music import Music
from models.cinema import Cinema
from datetime import datetime
from models.diary_model import DiaryEntry

api_routes = Blueprint('api_routes', __name__)

@api_routes.route('/api/notifications/unread', methods=['GET'])
@login_required
def unread_notifications_count():
    count = Notification.query.filter_by(user_id=current_user.user_id, read=False).count()
    return jsonify({'success': True, 'unread_count': count})

@api_routes.route('/api/notifications/latest', methods=['GET'])
@login_required
def latest_notifications():
    limit = request.args.get('limit', 10, type=int)
    notes = Notification.query.filter_by(user_id=current_user.user_id).order_by(Notification.created_at.desc()).limit(limit).all()
    return jsonify({'success': True, 'notifications': [
        {
            'id': n.notification_id,
            'message': n.message,
            'created_at': n.created_at.isoformat(),
            'read': n.read
        } for n in notes
    ]})

@api_routes.route('/api/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_notifications_read():
    Notification.query.filter_by(user_id=current_user.user_id, read=False).update({Notification.read: True})
    db.session.commit()
    return jsonify({'success': True})

# Fallback endpoint to prevent JSON errors in base template if messages API isn't implemented
@api_routes.route('/api/messages/unread', methods=['GET'])
@login_required
def unread_messages_count():
    return jsonify({'success': True, 'unread_count': 0})

@api_routes.route('/media/<int:media_id>/update-date', methods=['POST'])
@login_required
def update_media_date(media_id):
    media = UserMedia.query.filter_by(id=media_id, user_id=current_user.id).first_or_404()
    
    data = request.get_json()
    if not data or 'planned_date' not in data:
        return jsonify({'success': False, 'error': 'Missing planned_date'}), 400
    
    try:
        media.planned_date = datetime.strptime(data['planned_date'], '%Y-%m-%d')
        db.session.commit()
        return jsonify({'success': True})
    except ValueError:
        return jsonify({'success': False, 'error': 'Invalid date format'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@api_routes.route('/media/<int:media_id>/complete', methods=['POST'])
@login_required
def complete_media(media_id):
    media = UserMedia.query.filter_by(id=media_id, user_id=current_user.id).first_or_404()
    media.status = 'completed'
    media.completed_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'success': True})

@api_routes.route('/media/<int:media_id>/remove', methods=['POST'])
@login_required
def remove_media(media_id):
    media = UserMedia.query.filter_by(id=media_id, user_id=current_user.id).first_or_404()
    db.session.delete(media)
    db.session.commit()
    return jsonify({'success': True})

@api_routes.route('/media/plan', methods=['POST'])
@login_required
def plan_media():
    data = request.get_json()
    if not data or not all(k in data for k in ['media_type', 'title', 'planned_date']):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    try:
        media = UserMedia(
            user_id=current_user.id,
            media_type=data['media_type'],
            title=data['title'],
            planned_date=datetime.strptime(data['planned_date'], '%Y-%m-%d'),
            notes=data.get('notes', ''),
            status='planned'
        )
        db.session.add(media)
        db.session.commit()
        return jsonify({'success': True, 'media_id': media.id})
    except ValueError:
        return jsonify({'success': False, 'error': 'Invalid date format'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@api_routes.route('/api/lists/create', methods=['POST'])
@login_required
def create_list():
    try:
        name = request.form.get('name')
        description = request.form.get('description')
        is_private = request.form.get('is_private') == 'true'

        if not name:
            return jsonify({'success': False, 'message': 'List name is required'}), 400

        # Create new list
        new_list = List(
            user_id=current_user.id,
            name=name,
            description=description,
            is_private=is_private
        )

        db.session.add(new_list)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'List created successfully',
            'list_id': new_list.id
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@api_routes.route('/api/users', methods=['GET'])
@login_required
def get_users():
    """Get all users for sharing functionality"""
    users = User.query.filter(User.user_id != current_user.user_id).all()
    return jsonify([{
        'user_id': user.user_id,
        'username': user.username,
        'profile_picture': user.profile_picture
    } for user in users])

@api_routes.route('/api/follow/<int:user_id>', methods=['POST'])
@login_required
def follow_user(user_id):
    if user_id == current_user.user_id:
        return jsonify({'success': False, 'message': 'You cannot follow yourself'}), 400
    
    existing_follow = Follow.query.filter_by(
        follower_id=current_user.user_id,
        followed_id=user_id
    ).first()
    
    if existing_follow:
        db.session.delete(existing_follow)
        action = 'unfollowed'
    else:
        follow = Follow(follower_id=current_user.user_id, followed_id=user_id)
        db.session.add(follow)
        action = 'followed'
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'action': action,
        'message': f'Successfully {action} user'
    })

@api_routes.route('/api/lists/<int:list_id>/add', methods=['POST'])
@login_required
def add_to_list(list_id):
    data = request.get_json()
    media_type = data.get('media_type')
    media_id = data.get('media_id')
    
    if not media_type or not media_id:
        return jsonify({'success': False, 'message': 'Media type and ID are required'}), 400
    
    try:
        # Check if list belongs to current user
        list_obj = List.query.filter_by(list_id=list_id, user_id=current_user.user_id).first()
        if not list_obj:
            return jsonify({'success': False, 'message': 'List not found'}), 404
        
        # Create list item
        list_item = ListItem(list_id=list_id)
        
        if media_type == 'book':
            list_item.book_id = media_id
        elif media_type == 'music':
            list_item.music_id = media_id
        elif media_type == 'cinema':
            list_item.cinema_id = media_id
        else:
            return jsonify({'success': False, 'message': 'Invalid media type'}), 400
        
        db.session.add(list_item)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Item added to list successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@api_routes.route('/api/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('q', '')
    media_type = request.args.get('type', 'all')
    
    if not query:
        return jsonify({'success': False, 'message': 'Search query is required'}), 400
    
    results = []
    
    try:
        if media_type in ['all', 'books']:
            books = Book.query.filter(Book.title.ilike(f'%{query}%')).limit(10).all()
            results.extend([{
                'type': 'book',
                'id': book.book_id,
                'title': book.title,
                'author': book.author,
                'coverart': book.coverart
            } for book in books])
        
        if media_type in ['all', 'music']:
            music = Music.query.filter(Music.title.ilike(f'%{query}%')).limit(10).all()
            results.extend([{
                'type': 'music',
                'id': music.music_id,
                'title': music.title,
                'artist': music.artist,
                'coverart': music.coverart
            } for music in music])
        
        if media_type in ['all', 'cinema']:
            cinema = Cinema.query.filter(Cinema.title.ilike(f'%{query}%')).limit(10).all()
            results.extend([{
                'type': 'cinema',
                'id': cinema.cinema_id,
                'title': cinema.title,
                'director': cinema.director,
                'coverart': cinema.coverart
            } for cinema in cinema])
        
        return jsonify({
            'success': True,
            'results': results
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Diary API Routes
@api_routes.route('/api/diary', methods=['GET'])
@login_required
def get_diary_entries():
    """Get user's diary entries with filtering and pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    mood_filter = request.args.get('mood')
    tag_filter = request.args.get('tag')
    media_type_filter = request.args.get('media_type')
    search_query = request.args.get('search')
    
    query = DiaryEntry.query.filter_by(user_id=current_user.user_id)
    
    # Apply filters
    if mood_filter:
        query = query.filter_by(mood=mood_filter)
    
    if tag_filter:
        query = query.filter(DiaryEntry.tags.contains(tag_filter))
    
    if media_type_filter:
        if media_type_filter == 'standalone':
            query = query.filter_by(media_id=None)
        else:
            query = query.join(UserMedia).filter(UserMedia.media_type == media_type_filter)
    
    if search_query:
        query = query.filter(
            db.or_(
                DiaryEntry.content.contains(search_query),
                DiaryEntry.title.contains(search_query),
                DiaryEntry.tags.contains(search_query)
            )
        )
    
    # Order by creation date (newest first)
    query = query.order_by(DiaryEntry.created_at.desc())
    
    # Paginate
    pagination = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    entries = [entry.to_dict() for entry in pagination.items]
    
    return jsonify({
        'success': True,
        'entries': entries,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    })

@api_routes.route('/api/diary', methods=['POST'])
@login_required
def create_diary_entry():
    """Create a new diary entry"""
    data = request.get_json()
    
    if not data or 'content' not in data:
        return jsonify({'success': False, 'message': 'Content is required'}), 400
    
    try:
        entry = DiaryEntry(
            user_id=current_user.user_id,
            content=data['content'],
            title=data.get('title'),
            media_id=data.get('media_id'),
            mood=data.get('mood'),
            tags=','.join(data.get('tags', [])) if data.get('tags') else None,
            is_private=data.get('is_private', False)
        )
        
        db.session.add(entry)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Diary entry created successfully',
            'entry': entry.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@api_routes.route('/api/diary/<int:entry_id>', methods=['GET'])
@login_required
def get_diary_entry(entry_id):
    """Get a specific diary entry"""
    entry = DiaryEntry.query.filter_by(
        entry_id=entry_id, 
        user_id=current_user.user_id
    ).first()
    
    if not entry:
        return jsonify({'success': False, 'message': 'Entry not found'}), 404
    
    return jsonify({
        'success': True,
        'entry': entry.to_dict()
    })

@api_routes.route('/api/diary/<int:entry_id>', methods=['PUT'])
@login_required
def update_diary_entry(entry_id):
    """Update a diary entry"""
    entry = DiaryEntry.query.filter_by(
        entry_id=entry_id, 
        user_id=current_user.user_id
    ).first()
    
    if not entry:
        return jsonify({'success': False, 'message': 'Entry not found'}), 404
    
    data = request.get_json()
    
    if not data or 'content' not in data:
        return jsonify({'success': False, 'message': 'Content is required'}), 400
    
    try:
        entry.content = data['content']
        entry.title = data.get('title', entry.title)
        entry.mood = data.get('mood', entry.mood)
        entry.tags = ','.join(data.get('tags', [])) if data.get('tags') else entry.tags
        entry.is_private = data.get('is_private', entry.is_private)
        entry.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Diary entry updated successfully',
            'entry': entry.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@api_routes.route('/api/diary/<int:entry_id>', methods=['DELETE'])
@login_required
def delete_diary_entry(entry_id):
    """Delete a diary entry"""
    entry = DiaryEntry.query.filter_by(
        entry_id=entry_id, 
        user_id=current_user.user_id
    ).first()
    
    if not entry:
        return jsonify({'success': False, 'message': 'Entry not found'}), 404
    
    try:
        db.session.delete(entry)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Diary entry deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@api_routes.route('/api/diary/stats', methods=['GET'])
@login_required
def get_diary_stats():
    """Get diary statistics for the user"""
    total_entries = DiaryEntry.query.filter_by(user_id=current_user.user_id).count()
    
    # Mood statistics
    mood_stats = db.session.query(
        DiaryEntry.mood, 
        db.func.count(DiaryEntry.entry_id)
    ).filter_by(user_id=current_user.user_id).group_by(DiaryEntry.mood).all()
    
    # Monthly entries
    monthly_stats = db.session.query(
        db.func.date_format(DiaryEntry.created_at, '%Y-%m'),
        db.func.count(DiaryEntry.entry_id)
    ).filter_by(user_id=current_user.user_id).group_by(
        db.func.date_format(DiaryEntry.created_at, '%Y-%m')
    ).order_by(db.func.date_format(DiaryEntry.created_at, '%Y-%m')).all()
    
    # Most used tags
    tag_stats = db.session.query(
        DiaryEntry.tags
    ).filter_by(user_id=current_user.user_id).filter(
        DiaryEntry.tags.isnot(None)
    ).all()
    
    all_tags = []
    for tag_row in tag_stats:
        if tag_row[0]:
            all_tags.extend([tag.strip() for tag in tag_row[0].split(',')])
    
    from collections import Counter
    tag_counts = Counter(all_tags)
    top_tags = [{'tag': tag, 'count': count} for tag, count in tag_counts.most_common(10)]
    
    return jsonify({
        'success': True,
        'stats': {
            'total_entries': total_entries,
            'mood_stats': [{'mood': mood, 'count': count} for mood, count in mood_stats if mood],
            'monthly_stats': [{'month': month, 'count': count} for month, count in monthly_stats],
            'top_tags': top_tags
        }
    })

@api_routes.route('/api/diary/moods', methods=['GET'])
@login_required
def get_available_moods():
    """Get list of available moods"""
    moods = ['happy', 'sad', 'excited', 'calm', 'anxious', 'inspired', 'tired', 'energetic', 'neutral', 'grateful', 'frustrated', 'peaceful']
    return jsonify({
        'success': True,
        'moods': moods
    })