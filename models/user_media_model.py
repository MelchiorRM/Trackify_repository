from models.user_model import db
from datetime import datetime

class UserMedia(db.Model):
    __tablename__ = 'user_media'
    user_media_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    cinema_id = db.Column(db.Integer, db.ForeignKey('cinema.cinema_id'))
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'))
    music_id = db.Column(db.Integer, db.ForeignKey('music.music_id'))
    media_type = db.Column(db.Enum('book', 'music', 'cinema', name='media_type'), nullable=False)
    done = db.Column(db.Boolean, default=False)
    planned = db.Column(db.Boolean, default=False)
    planned_date = db.Column(db.Date, default=None)
    date_consumed = db.Column(db.DateTime, default=None)
    review = db.Column(db.Text, default=None)
    rating = db.Column(db.DECIMAL(2, 1), default=None)
    notes = db.Column(db.Text, default=None)
    tags = db.Column(db.JSON, default=list)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'book_id', 'music_id', 'cinema_id', name='unique_media'),)

    # Relationships
    book = db.relationship('Book', backref='user_media')
    cinema = db.relationship('Cinema', backref='user_media')
    music = db.relationship('Music', backref='user_media')

    def __init__(self, user_id, media_type, cinema_id=None, book_id=None, music_id=None, done=False, planned=False, planned_date=None, date_consumed=None, review=None, rating=None, notes=None, tags=None):
        self.user_id = user_id
        self.media_type = media_type
        self.cinema_id = cinema_id
        self.book_id = book_id
        self.music_id = music_id
        self.done = done
        self.planned = planned
        self.planned_date = planned_date
        self.date_consumed = date_consumed
        self.review = review
        self.rating = rating
        self.notes = notes
        self.tags = tags if tags is not None else []
        self.created_at = datetime.utcnow()

    @property
    def title(self):
        """Get the title of the media based on type"""
        if self.media_type == 'book' and self.book:
            return self.book.title
        elif self.media_type == 'cinema' and self.cinema:
            return self.cinema.title
        elif self.media_type == 'music' and self.music:
            return self.music.title
        return "Unknown Title"

    @property
    def author(self):
        """Get the author/director/artist based on media type"""
        if self.media_type == 'book' and self.book:
            return self.book.author
        elif self.media_type == 'cinema' and self.cinema:
            return self.cinema.director
        elif self.media_type == 'music' and self.music:
            return self.music.artist
        return "Unknown"

    @property
    def director(self):
        """Get the director for cinema"""
        if self.media_type == 'cinema' and self.cinema:
            return self.cinema.director
        return "Unknown"

    @property
    def artist(self):
        """Get the artist for music"""
        if self.media_type == 'music' and self.music:
            return self.music.artist
        return "Unknown"

    def to_dict(self):
        """Convert UserMedia to dictionary for API responses"""
        return {
            'user_media_id': self.user_media_id,
            'user_id': self.user_id,
            'media_type': self.media_type,
            'book_id': self.book_id,
            'music_id': self.music_id,
            'cinema_id': self.cinema_id,
            'title': self.title,
            'author': self.author,
            'director': self.director,
            'artist': self.artist,
            'done': self.done,
            'planned': self.planned,
            'planned_date': self.planned_date.isoformat() if self.planned_date else None,
            'date_consumed': self.date_consumed.isoformat() if self.date_consumed else None,
            'review': self.review,
            'rating': float(self.rating) if self.rating else None,
            'notes': self.notes,
            'tags': self.tags,
            'created_at': self.created_at.isoformat()
        }