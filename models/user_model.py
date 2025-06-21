from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from datetime import datetime
db = SQLAlchemy()
bcrypt = Bcrypt()
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    join_date = db.Column(db.DateTime, default=datetime.utcnow)
    profile_picture = db.Column(db.String(256), nullable=True)
    bio = db.Column(db.Text, default=None)
    theme = db.Column(db.String(20), default='light')
    notifications_enabled = db.Column(db.Boolean, default=True)
    email_notifications = db.Column(db.Boolean, default=True)

    # Add new relationships
    ratings = db.relationship('Rating', backref='user', lazy='dynamic')
    reviews = db.relationship('Review', backref='user', lazy='dynamic')
    custom_lists = db.relationship('CustomList', backref='creator', lazy='dynamic')
    messages_sent = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy='dynamic')
    messages_received = db.relationship('Message', foreign_keys='Message.recipient_id', backref='recipient', lazy='dynamic')
    user_media = db.relationship('UserMedia', backref='user', lazy='dynamic')
    
    # Following relationships
    following = db.relationship(
        'Follow',
        foreign_keys='Follow.follower_id',
        backref=db.backref('follower', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    followers = db.relationship(
        'Follow',
        foreign_keys='Follow.followed_id',
        backref=db.backref('followed', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def __init__(self, username, password, email, profile_picture, bio=None):
        self.username = username
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        self.email = email
        self.profile_picture = profile_picture
        self.bio = bio if bio else ''
        
    def get_id(self):
        return self.user_id

    def is_following(self, user):
        return self.following.filter_by(followed_id=user.user_id).first() is not None

    def follow(self, user):
        if not self.is_following(user):
            follow = Follow(follower_id=self.user_id, followed_id=user.user_id)
            db.session.add(follow)
            db.session.commit()

    def unfollow(self, user):
        follow = self.following.filter_by(followed_id=user.user_id).first()
        if follow:
            db.session.delete(follow)
            db.session.commit()