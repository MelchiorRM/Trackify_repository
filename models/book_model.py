from models.user_model import db

class Book(db.Model):
    __tablename__ = 'books'
    book_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    genre = db.Column(db.String(100))
    year = db.Column(db.Integer)
    language = db.Column(db.String(100))
    publisher = db.Column(db.String(100))
    country = db.Column(db.String(100))
    description = db.Column(db.Text)
    coverart = db.Column(db.String(255))

    def __init__(self, title, author, genre, year, language, publisher, country,description, coverart):
        self.title = title
        self.author = author
        self.genre = genre
        self.year = year
        self.language = language
        self.publisher = publisher
        self.country = country
        self.description = description
        self.coverart = coverart