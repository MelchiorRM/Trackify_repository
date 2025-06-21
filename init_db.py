from app import create_app
from models.user_model import db
from models.social_model import Post, Like, Comment, Follow, Notification, Rating, Review, Message, CustomList
from models.user_media_model import UserMedia
from models.book_model import Book
from models.music_model import Music
from models.cinema_model import Cinema
from models.diary_model import DiaryEntry

def init_database():
    app = create_app()
    with app.app_context():
        # Drop all tables
        db.drop_all()
        print("Dropped all existing tables")
        
        # Create all tables
        db.create_all()
        print("Created all tables with new schema")
        
        print("Database initialization completed!")

if __name__ == "__main__":
    init_database() 