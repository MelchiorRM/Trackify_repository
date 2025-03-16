from models.user_model import db
class Cinema(db.Model):
    __tablename__ = 'cinema'
    
    cinema_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    genre = db.Column(db.String(100))
    year = db.Column(db.Integer)
    country = db.Column(db.String(100))
    director = db.Column(db.String(255))
    type = db.Column(db.String(100))
    language = db.Column(db.String(100))
    description = db.Column(db.Text)
    coverart = db.Column(db.String(255))

    def __init__(self, title, genre, year, country, director, type, language, description, coverart):
        self.title = title
        self.genre = genre
        self.year = year
        self.country = country
        self.director = director
        self.type = type
        self.language = language
        self.description = description
        self.coverart = coverart