from models.user_model import db
class Music(db.Model):
    __tablename__ = 'music'
    
    music_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    artist = db.Column(db.String(255), nullable=False)
    genre = db.Column(db.String(100))
    year = db.Column(db.Integer)
    language = db.Column(db.String(100))
    label = db.Column(db.String(100))
    country = db.Column(db.String(100))
    description = db.Column(db.Text)
    coverart = db.Column(db.String(255))

    def __init__(self, title, artist, genre, year, language, label, country, description, coverart):
        self.title = title
        self.artist = artist
        self.genre = genre
        self.year = year
        self.language = language
        self.label = label
        self.country = country
        self.description = description
        self.coverart = coverart