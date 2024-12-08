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
    DEBUG = True