from models.user_model import db
from datetime import datetime
from sqlalchemy import event
from sqlalchemy.orm import Session
from flask import current_app
from models.user_media_model import UserMedia
from models.user_model import User

class Follow(db.Model):
    __tablename__ = 'follows'
    follow_id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)

    __table_args__ = (db.UniqueConstraint('follower_id', 'followed_id', name='unique_follow'),)
    
    def __init__(self, follower_id, followed_id):
        self.follower_id = follower_id
        self.followed_id = followed_id

class Like(db.Model):
    __tablename__ = 'likes'
    like_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    user_media_id = db.Column(db.Integer, db.ForeignKey('user_media.user_media_id'), nullable=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.post_id'), nullable=True)
    
    __table_args__ = (db.UniqueConstraint('user_id','user_media_id', name='unique_like'),)
    
    def __init__(self, user_id, user_media_id=None, post_id=None):
        self.user_id = user_id
        self.user_media_id = user_media_id
        self.post_id = post_id

class Comment(db.Model):
    __tablename__ = 'comments'
    comment_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    user_media_id = db.Column(db.Integer, db.ForeignKey('user_media.user_media_id'), nullable=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.post_id'), nullable=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='comments')

    def __init__(self, user_id, content, user_media_id=None, post_id=None):
        self.user_id = user_id
        self.content = content
        self.user_media_id = user_media_id
        self.post_id = post_id
        self.created_at = datetime.utcnow()

class Post(db.Model):
    __tablename__ = 'posts'
    post_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    media_type = db.Column(db.Enum('cinema', 'music', 'book'), nullable=True)
    media_id = db.Column(db.Integer, nullable=True)  # cinema_id, music_id, or book_id
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='posts')
    likes = db.relationship('Like', backref='post', lazy='dynamic', foreign_keys='Like.post_id')
    comments = db.relationship('Comment', backref='post', lazy='dynamic', order_by='Comment.created_at.desc()', foreign_keys='Comment.post_id')
    
    def __init__(self, user_id, content, media_type=None, media_id=None):
        self.user_id = user_id
        self.content = content
        self.media_type = media_type
        self.media_id = media_id
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

class List(db.Model):
    __tablename__ = 'lists'
    list_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

    def __init__(self, user_id, name, description):
        self.user_id = user_id
        self.name = name
        self.description = description

class ListItem(db.Model):
    __tablename__ = 'list_items'
    list_item_id = db.Column(db.Integer, primary_key=True)
    list_id = db.Column(db.Integer, db.ForeignKey('lists.list_id'))
    cinema_id = db.Column(db.Integer, db.ForeignKey('cinema.cinema_id'))
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'))
    music_id = db.Column(db.Integer, db.ForeignKey('music.music_id'))

    def __init__(self, list_id, cinema_id=None, book_id=None, music_id=None):
        self.list_id = list_id
        self.cinema_id = cinema_id
        self.book_id = book_id
        self.music_id = music_id

class Notification(db.Model):
    __tablename__ = 'notifications'
    notification_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)

    def __init__(self, user_id, message):
        self.user_id = user_id
        self.message = message
        self.created_at = datetime.utcnow()

@event.listens_for(Session, "before_commit")
def create_notifications(session):
    # Check for pending notifications in the session
    if hasattr(current_app, "_pending_notifications"):
        for notification in current_app._pending_notifications:
            session.add(notification)
        del current_app._pending_notifications

@event.listens_for(Like, "after_insert")
def like_notif(mapper, connection, target):
    if target.user_media_id:
        # Media like notification
        entry = db.session.get(UserMedia, target.user_media_id)
        if entry and entry.user_id != target.user_id:
            notification = Notification(
                user_id=entry.user_id,
                message=f"{db.session.get(User, target.user_id).username} liked your {entry.media_type}"
            )
            if not hasattr(current_app, "_pending_notifications"):
                current_app._pending_notifications = []
            current_app._pending_notifications.append(notification)
    elif target.post_id:
        # Post like notification
        post = db.session.get(Post, target.post_id)
        if post and post.user_id != target.user_id:
            notification = Notification(
                user_id=post.user_id,
                message=f"{db.session.get(User, target.user_id).username} liked your post"
            )
            if not hasattr(current_app, "_pending_notifications"):
                current_app._pending_notifications = []
            current_app._pending_notifications.append(notification)

@event.listens_for(Comment, "after_insert")
def comment_notif(mapper, connection, target):
    if target.user_media_id:
        # Media comment notification
        entry = db.session.get(UserMedia, target.user_media_id)
        if entry and entry.user_id != target.user_id:
            notification = Notification(
                user_id=entry.user_id,
                message=f"{db.session.get(User, target.user_id).username} commented on your {entry.media_type}"
            )
            if not hasattr(current_app, "_pending_notifications"):
                current_app._pending_notifications = []
            current_app._pending_notifications.append(notification)
    elif target.post_id:
        # Post comment notification
        post = db.session.get(Post, target.post_id)
        if post and post.user_id != target.user_id:
            notification = Notification(
                user_id=post.user_id,
                message=f"{db.session.get(User, target.user_id).username} commented on your post"
            )
            if not hasattr(current_app, "_pending_notifications"):
                current_app._pending_notifications = []
            current_app._pending_notifications.append(notification)

@event.listens_for(Follow, "after_insert")
def follow_notif(mapper, connection, target):
    notification = Notification(
        user_id=target.followed_id,
        message=f"{db.session.get(User, target.follower_id).username} started following you"
    )
    if not hasattr(current_app, "_pending_notifications"):
        current_app._pending_notifications = []
    current_app._pending_notifications.append(notification)

class Rating(db.Model):
    __tablename__ = 'ratings'
    rating_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    user_media_id = db.Column(db.Integer, db.ForeignKey('user_media.user_media_id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Review(db.Model):
    __tablename__ = 'reviews'
    review_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    user_media_id = db.Column(db.Integer, db.ForeignKey('user_media.user_media_id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Message(db.Model):
    __tablename__ = 'messages'
    message_id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_media_id = db.Column(db.Integer, db.ForeignKey('user_media.user_media_id'))  # For sharing media
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

class CustomList(db.Model):
    __tablename__ = 'custom_lists'
    list_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_private = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)