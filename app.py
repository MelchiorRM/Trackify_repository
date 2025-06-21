from flask import Flask
from flask_login import LoginManager
from routes.user_routes import user_routes
from routes.media_routes import media_routes
from routes.main_routes import main_routes
from routes.api_routes import api_routes
from routes.post_routes import post_routes
from routes.message_routes import message_routes
from models.user_model import db, User
from config import Config
from flask_session import Session
from flask_bcrypt import Bcrypt
from error import error_handler

bcrypt = Bcrypt()
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    Config.init_app(app)  # Initialize config (create directories)
    
    db.init_app(app)
    bcrypt.init_app(app)
    Session(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'user_routes.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    app.register_blueprint(user_routes)
    app.register_blueprint(media_routes)
    app.register_blueprint(main_routes)
    app.register_blueprint(api_routes)
    app.register_blueprint(post_routes)
    app.register_blueprint(message_routes)

    with app.app_context():
        db.create_all()

    error_handler(app)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host="0.0.0.0", port=5000)