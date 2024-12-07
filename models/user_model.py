from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_manager
from flask_bcrypt import Bcrypt
from datetime import datetime
db = SQLAlchemy()
bcrypt = Bcrypt()
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    join_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, username, password, email):
        self.username = username
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        self.email = email