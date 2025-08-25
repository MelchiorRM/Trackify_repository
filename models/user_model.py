from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
import secrets
import string
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
    
    # Password reset fields
    reset_token = db.Column(db.String(100), unique=True, nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)

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

    def __init__(self, username, password, email, profile_picture=None, bio=None):
        self.username = username
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        self.email = email
        # Always set a default profile picture if none provided
        self.profile_picture = profile_picture if profile_picture else 'defaults/user.png'
        self.bio = bio if bio else ''
        
    def get_id(self):
        return self.user_id

    def is_following(self, user):
        return self.following.filter_by(followed_id=user.user_id).first() is not None

    def follow(self, user):
        if not self.is_following(user):
            from models.social_model import Follow
            follow = Follow(follower_id=self.user_id, followed_id=user.user_id)
            db.session.add(follow)
            db.session.commit()

    def unfollow(self, user):
        follow = self.following.filter_by(followed_id=user.user_id).first()
        if follow:
            db.session.delete(follow)
            db.session.commit()
    
    def generate_reset_token(self):
        """Generate a secure reset token"""
        self.reset_token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
        self.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)  # Token expires in 1 hour
        return self.reset_token
    
    def verify_reset_token(self, token):
        """Verify if the reset token is valid and not expired"""
        if (self.reset_token == token and 
            self.reset_token_expiry and 
            self.reset_token_expiry > datetime.utcnow()):
            return True
        return False
    
    def clear_reset_token(self):
        """Clear the reset token after use"""
        self.reset_token = None
        self.reset_token_expiry = None
    
    @property
    def profile_picture_url(self):
        """Return the profile picture URL, ensuring default is used if none set"""
        if not self.profile_picture or self.profile_picture == '':
            return 'defaults/user.png'
        return self.profile_picture