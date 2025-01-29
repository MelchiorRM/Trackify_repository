# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or '8da15c2b8946c4261a4c1516b4c86e19'  # Use environment variable for production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'mysql+mysqlconnector://root:Mysql123%40@localhost/trackifydb'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_TYPE = 'filesystem'  # Use filesystem for session storage (you can change this)
    SESSION_PERMANENT = False  # Sessions expire when the browser closes
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes (30 * 60 seconds)
    GOOGLE_BOOKS_API_KEY = os.environ.get('GOOGLE_BOOKS_API_KEY') or 'AIzaSyA2A-qxj3CZhKDMNni4vcK3EA1rSnj25Fg'
    TMDB_API_KEY = os.environ.get('TMDB_API_KEY') or '22f25a5ae58d199051d00c89d1eb7550'
    SPOTIFY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID') or '15a15c13a1d649f2a5989067b2cb141e'
    SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET') or '05cd351353f640ba9d6c7a0e232768a0'
    DEBUG = True