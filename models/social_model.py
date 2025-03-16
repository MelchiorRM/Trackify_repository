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
    user_media_id = db.Column(db.Integer, db.ForeignKey('user_media.user_media_id'), nullable=False)
    
    __table_args__ = (db.UniqueConstraint('user_id','user_media_id', name='unique_like'),)
    
    def __init__(self, user_id, user_media_id):
        self.user_id = user_id
        self.user_media_id = user_media_id

class Comment(db.Model):
    __tablename__ = 'comments'
    comment_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    user_media_id = db.Column(db.Integer, db.ForeignKey('user_media.user_media_id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='comments')

    def __init__(self, user_id, user_media_id, content):
        self.user_id = user_id
        self.user_media_id = user_media_id
        self.content = content
        self.created_at = datetime.utcnow()

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
    entry = db.session.get(UserMedia, target.user_media_id)
    if entry and entry.user_id != target.user_id:
        notification = Notification(
            user_id=entry.user_id,
            message=f"{db.session.get(User, target.user_id).username} liked your {entry.media_type}"
        )
        if not hasattr(current_app, "_pending_notifications"):
            current_app._pending_notifications = []
        current_app._pending_notifications.append(notification)

@event.listens_for(Comment, "after_insert")
def comment_notif(mapper, connection, target):
    entry = db.session.get(UserMedia, target.user_media_id)
    if entry and entry.user_id != target.user_id:
        notification = Notification(
            user_id=entry.user_id,
            message=f"{db.session.get(User, target.user_id).username} commented on your {entry.media_type}"
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