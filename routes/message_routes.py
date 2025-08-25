from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models.social_model import Message, User, db
from models.user_media_model import UserMedia
from models.books import Book
from models.music import Music
from models.cinema import Cinema
from datetime import datetime
from sqlalchemy import and_, or_

message_routes = Blueprint('message_routes', __name__)

@message_routes.route('/messages', methods=['GET'])
@login_required
def messages():
    """Main messages page - shows conversations list"""
    # Get all conversations (users you've messaged or received messages from)
    conversations = db.session.query(User).join(
        Message, or_(
            and_(Message.sender_id == User.user_id, Message.recipient_id == current_user.user_id),
            and_(Message.recipient_id == User.user_id, Message.sender_id == current_user.user_id)
        )
    ).filter(User.user_id != current_user.user_id).distinct().all()
    
    # Get latest message for each conversation
    conversation_data = []
    for user in conversations:
        latest_message = Message.query.filter(
            or_(
                and_(Message.sender_id == current_user.user_id, Message.recipient_id == user.user_id),
                and_(Message.sender_id == user.user_id, Message.recipient_id == current_user.user_id)
            )
        ).order_by(Message.created_at.desc()).first()
        
        # Count unread messages
        unread_count = Message.query.filter(
            and_(
                Message.sender_id == user.user_id,
                Message.recipient_id == current_user.user_id,
                Message.is_read == False
            )
        ).count()
        
        conversation_data.append({
            'user': user,
            'latest_message': latest_message,
            'unread_count': unread_count
        })
    
    # Sort by latest message time
    conversation_data.sort(key=lambda x: x['latest_message'].created_at if x['latest_message'] else datetime.min, reverse=True)
    
    return render_template('messages.html', conversations=conversation_data)

@message_routes.route('/messages/<int:user_id>', methods=['GET'])
@login_required
def conversation(user_id):
    """Individual conversation view"""
    other_user = User.query.get_or_404(user_id)
    
    if other_user.user_id == current_user.user_id:
        flash('You cannot message yourself', 'error')
        return redirect(url_for('message_routes.messages'))
    
    # Get all messages between these users
    messages = Message.query.filter(
        or_(
            and_(Message.sender_id == current_user.user_id, Message.recipient_id == user_id),
            and_(Message.sender_id == user_id, Message.recipient_id == current_user.user_id)
        )
    ).order_by(Message.created_at.asc()).all()
    
    # Mark messages as read
    unread_messages = Message.query.filter(
        and_(
            Message.sender_id == user_id,
            Message.recipient_id == current_user.user_id,
            Message.is_read == False
        )
    ).all()
    
    for message in unread_messages:
        message.is_read = True
    
    db.session.commit()
    
    # Support partial rendering for AJAX load inside messages page
    if request.args.get('partial') == '1':
        return render_template('partials/conversation_inner.html', other_user=other_user, messages=messages)
    return render_template('conversation.html', other_user=other_user, messages=messages)

@message_routes.route('/messages/<int:user_id>/send', methods=['POST'])
@login_required
def send_message(user_id):
    """Send a message to a user"""
    other_user = User.query.get_or_404(user_id)
    
    if other_user.user_id == current_user.user_id:
        return jsonify({'success': False, 'error': 'You cannot message yourself'}), 400
    
    content = request.json.get('content', '').strip()
    media_type = request.json.get('media_type')
    media_id = request.json.get('media_id')
    
    if not content:
        return jsonify({'success': False, 'error': 'Message content is required'}), 400
    
    # Create message
    message = Message(
        sender_id=current_user.user_id,
        recipient_id=user_id,
        content=content
    )
    
    # Add media reference if provided
    if media_type and media_id:
        message.user_media_id = media_id
    
    db.session.add(message)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': {
            'id': message.message_id,
            'content': message.content,
            'created_at': message.created_at.strftime('%Y-%m-%d %H:%M'),
            'sender': {
                'username': current_user.username,
                'profile_picture': current_user.profile_picture
            }
        }
    })

@message_routes.route('/api/messages/<int:user_id>', methods=['GET'])
@login_required
def get_messages(user_id):
    """Get messages for a conversation (AJAX)"""
    other_user = User.query.get_or_404(user_id)
    
    if other_user.user_id == current_user.user_id:
        return jsonify({'success': False, 'error': 'Invalid user'}), 400
    
    # Get messages
    messages = Message.query.filter(
        or_(
            and_(Message.sender_id == current_user.user_id, Message.recipient_id == user_id),
            and_(Message.sender_id == user_id, Message.recipient_id == current_user.user_id)
        )
    ).order_by(Message.created_at.asc()).all()
    
    # Mark as read
    unread_messages = Message.query.filter(
        and_(
            Message.sender_id == user_id,
            Message.recipient_id == current_user.user_id,
            Message.is_read == False
        )
    ).all()
    
    for message in unread_messages:
        message.is_read = True
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'messages': [{
            'id': msg.message_id,
            'content': msg.content,
            'created_at': msg.created_at.strftime('%Y-%m-%d %H:%M'),
            'is_read': msg.is_read,
            'sender_id': msg.sender_id,
            'sender': {
                'username': msg.sender.username,
                'profile_picture': msg.sender.profile_picture
            },
            'media_info': get_media_info(msg.user_media_id) if msg.user_media_id else None
        } for msg in messages]
    })

@message_routes.route('/api/messages/unread', methods=['GET'])
@login_required
def get_unread_count():
    """Get total unread message count"""
    unread_count = Message.query.filter(
        and_(
            Message.recipient_id == current_user.user_id,
            Message.is_read == False
        )
    ).count()
    
    return jsonify({
        'success': True,
        'unread_count': unread_count
    })

@message_routes.route('/api/messages/search', methods=['GET'])
@login_required
def search_users():
    """Search users for messaging"""
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify({'success': False, 'error': 'Search query required'}), 400
    
    users = User.query.filter(
        and_(
            User.username.ilike(f'%{query}%'),
            User.user_id != current_user.user_id
        )
    ).limit(10).all()
    
    return jsonify({
        'success': True,
        'users': [{
            'user_id': user.user_id,
            'username': user.username,
            'profile_picture': user.profile_picture
        } for user in users]
    })

@message_routes.route('/api/messages/share-media', methods=['POST'])
@login_required
def share_media():
    """Share media via message"""
    recipient_id = request.json.get('recipient_id')
    media_type = request.json.get('media_type')
    media_id = request.json.get('media_id')
    message_text = request.json.get('message', '')
    
    if not all([recipient_id, media_type, media_id]):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    # Get media info
    media_info = get_media_info_by_type(media_type, media_id)
    if not media_info:
        return jsonify({'success': False, 'error': 'Media not found'}), 404
    
    # Create message
    content = f"Check out this {media_type}:\n\n"
    if message_text:
        content += f"{message_text}\n\n"
    content += f"Title: {media_info['title']}"
    
    message = Message(
        sender_id=current_user.user_id,
        recipient_id=recipient_id,
        content=content,
        user_media_id=media_id
    )
    
    db.session.add(message)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Media shared successfully!'
    })

def get_media_info(user_media_id):
    """Get media info from user_media_id"""
    user_media = UserMedia.query.get(user_media_id)
    if not user_media:
        return None
    
    if user_media.media_type == 'book':
        media = Book.query.get(user_media.book_id)
        return {
            'type': 'book',
            'title': media.title if media else 'Unknown Book',
            'author': media.author if media else 'Unknown Author',
            'coverart': media.coverart if media else None
        }
    elif user_media.media_type == 'music':
        media = Music.query.get(user_media.music_id)
        return {
            'type': 'music',
            'title': media.title if media else 'Unknown Music',
            'artist': media.artist if media else 'Unknown Artist',
            'coverart': media.coverart if media else None
        }
    elif user_media.media_type == 'cinema':
        media = Cinema.query.get(user_media.cinema_id)
        return {
            'type': 'cinema',
            'title': media.title if media else 'Unknown Movie',
            'director': media.director if media else 'Unknown Director',
            'coverart': media.coverart if media else None
        }
    
    return None

def get_media_info_by_type(media_type, media_id):
    """Get media info by type and ID"""
    if media_type == 'book':
        media = Book.query.get(media_id)
        return {
            'title': media.title if media else 'Unknown Book',
            'author': media.author if media else 'Unknown Author'
        }
    elif media_type == 'music':
        media = Music.query.get(media_id)
        return {
            'title': media.title if media else 'Unknown Music',
            'artist': media.artist if media else 'Unknown Artist'
        }
    elif media_type == 'cinema':
        media = Cinema.query.get(media_id)
        return {
            'title': media.title if media else 'Unknown Movie',
            'director': media.director if media else 'Unknown Director'
        }
    
    return None 