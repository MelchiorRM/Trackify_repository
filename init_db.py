from app import create_app
from models.user_model import db, User
import os

def init_database():
    app = create_app()
    with app.app_context():
        # Create database tables
        db.create_all()
        
        # Ensure default profile picture directory exists
        static_dir = os.path.join(app.root_path, 'static')
        defaults_dir = os.path.join(static_dir, 'defaults')
        profile_pictures_dir = os.path.join(static_dir, 'profile_pictures')
        
        # Create directories if they don't exist
        os.makedirs(defaults_dir, exist_ok=True)
        os.makedirs(profile_pictures_dir, exist_ok=True)
        
        # Check if default user.png exists in static directory
        default_user_png = os.path.join(defaults_dir, 'user.png')
        if not os.path.exists(default_user_png):
            print("Warning: static/defaults/user.png not found. Please ensure the default profile picture exists.")
            print(f"Expected location: {default_user_png}")
        else:
            print("Default profile picture found.")
        
        print("Database initialized successfully!")
        print("Directories created:")
        print(f"  - {defaults_dir}")
        print(f"  - {profile_pictures_dir}")

if __name__ == '__main__':
    init_database() 