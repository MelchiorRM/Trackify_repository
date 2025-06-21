from models.user_model import db
from datetime import datetime

class DiaryEntry(db.Model):
    __tablename__ = 'diary_entries'
    
    entry_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    media_id = db.Column(db.Integer, db.ForeignKey('user_media.user_media_id'), nullable=True)  # Optional link to media
    title = db.Column(db.String(200))  # Optional title for standalone entries
    content = db.Column(db.Text, nullable=False)
    mood = db.Column(db.String(50))  # happy, sad, excited, neutral, etc.
    tags = db.Column(db.Text)  # Comma-separated tags
    is_private = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('diary_entries', lazy=True))
    media = db.relationship('UserMedia', backref=db.backref('diary_entries', lazy=True))

    def __init__(self, user_id, content, title=None, media_id=None, mood=None, tags=None, is_private=False):
        self.user_id = user_id
        self.content = content
        self.title = title
        self.media_id = media_id
        self.mood = mood
        self.tags = tags
        self.is_private = is_private
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        """Convert entry to dictionary for API responses"""
        return {
            'entry_id': self.entry_id,
            'user_id': self.user_id,
            'media_id': self.media_id,
            'title': self.title,
            'content': self.content,
            'mood': self.mood,
            'tags': self.tags.split(',') if self.tags else [],
            'is_private': self.is_private,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'media': self.media.to_dict() if self.media else None,
            'user': {
                'user_id': self.user.user_id,
                'username': self.user.username,
                'profile_picture': self.user.profile_picture
            } if self.user else None
        } 