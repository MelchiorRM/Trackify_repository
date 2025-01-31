from flask import Flask
from flask_login import LoginManager
from routes.user_routes import user_routes
from routes.media_routes import media_routes
from models.user_model import db, User
from config import Config
from flask_session import Session
from flask_bcrypt import Bcrypt
from error import error_handler

bcrypt = Bcrypt()
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    bcrypt.init_app(app)
    Session(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    app.register_blueprint(user_routes)
    app.register_blueprint(media_routes)

    with app.app_context():
        db.create_all()

    error_handler(app)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host="0.0.0.0", port=5000)