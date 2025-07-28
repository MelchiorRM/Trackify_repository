# config.py
import os
from datetime import timedelta

class Config:
    # Basic Flask config
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Database config
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///trackify.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File upload config
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  # Allowed image file types
    
    # Session config
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'flask_session')
    
    # Security config
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY') or 'your-csrf-secret-key-here'
    
    # Email config (if needed later)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Create necessary directories
    @staticmethod
    def init_app(app):
        # Create upload directory if it doesn't exist
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        # Create session directory if it doesn't exist
        os.makedirs(Config.SESSION_FILE_DIR, exist_ok=True)

    SESSION_PERMANENT = False  # Sessions expire when the browser closes
    GOOGLE_BOOKS_API_KEY = os.environ.get('GOOGLE_BOOKS_API_KEY') or 'AIzaSyA2A-qxj3CZhKDMNni4vcK3EA1rSnj25Fg'
    TMDB_API_KEY = os.environ.get('TMDB_API_KEY') or '22f25a5ae58d199051d00c89d1eb7550'
    SPOTIFY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID') or '15a15c13a1d649f2a5989067b2cb141e'
    SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET') or '05cd351353f640ba9d6c7a0e232768a0'
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY') or 'AIzaSyAPmeqpfb6lcbSdO5fOaawRta7-u6GX0y4'
    DEBUG = True