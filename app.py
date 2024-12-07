from flask import Flask
from flask_login import LoginManager
from routes.user_routes import user_routes
from routes.media_routes import media_routes
from models.user_model import db, User


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '8da15c2b8946c4261a4c1516b4c86e19'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Mysql123%40@localhost/trackifydb'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    login_manager = LoginManager()
    login_manager.init_app(app)
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    app.register_blueprint(user_routes)
    app.register_blueprint(media_routes)

    with app.app_context():
        db.create_all()
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
