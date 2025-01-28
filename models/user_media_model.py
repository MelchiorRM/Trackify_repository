from models.user_model import db

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

    __table_args__ = (db.UniqueConstraint('user_id', 'book_id', 'music_id', 'cinema_id', name='unique_media'),)

    def __init__(self, user_id, media_type, cinema_id=None, book_id=None, music_id=None, done=False, planned=False):
        self.user_id = user_id
        self.media_type = media_type
        self.cinema_id = cinema_id
        self.book_id = book_id
        self.music_id = music_id
        self.done = done
        self.planned = planned