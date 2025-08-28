#!/usr/bin/env python3
"""
Database migration script utilities
 - Adds password reset columns to users table
 - Adds planner columns to user_media table (planned_date, notes)
"""

import sqlite3
import os
from datetime import datetime

def migrate_password_reset():
    """Add password reset columns to the users table"""
    
    # Database file path
    db_path = 'instance/trackify.db'
    
    if not os.path.exists(db_path):
        print(f"Database file not found at {db_path}")
        print("Please run the application first to create the database.")
        return False
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add reset_token column if it doesn't exist
        if 'reset_token' not in columns:
            print("Adding reset_token column...")
            cursor.execute("ALTER TABLE users ADD COLUMN reset_token VARCHAR(100)")
            print("✓ reset_token column added")
        else:
            print("✓ reset_token column already exists")
        
        # Add reset_token_expiry column if it doesn't exist
        if 'reset_token_expiry' not in columns:
            print("Adding reset_token_expiry column...")
            cursor.execute("ALTER TABLE users ADD COLUMN reset_token_expiry DATETIME")
            print("✓ reset_token_expiry column added")
        else:
            print("✓ reset_token_expiry column already exists")
        
        # Create index on reset_token for better performance
        try:
            cursor.execute("CREATE INDEX idx_users_reset_token ON users(reset_token)")
            print("✓ Index created on reset_token column")
        except sqlite3.OperationalError:
            print("✓ Index already exists on reset_token column")
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print("\n✅ Password reset migration completed successfully!")
        print("The users table now supports password reset functionality.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        return False


def migrate_user_media_planner_columns():
    """Add planned_date and notes columns to user_media if missing"""
    db_path = 'instance/trackify.db'
    if not os.path.exists(db_path):
        print(f"Database file not found at {db_path}")
        return False
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(user_media)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'media_type' not in columns:
            print("Adding media_type to user_media...")
            cursor.execute("ALTER TABLE user_media ADD COLUMN media_type TEXT")
            print("✓ media_type added")
        else:
            print("✓ media_type already exists")

        if 'tags' not in columns:
            print("Adding tags to user_media...")
            cursor.execute("ALTER TABLE user_media ADD COLUMN tags TEXT")
            print("✓ tags added")
        else:
            print("✓ tags already exists")

        if 'planned_date' not in columns:
            print("Adding planned_date to user_media...")
            cursor.execute("ALTER TABLE user_media ADD COLUMN planned_date DATE")
            print("✓ planned_date added")
        else:
            print("✓ planned_date already exists")

        if 'notes' not in columns:
            print("Adding notes to user_media...")
            cursor.execute("ALTER TABLE user_media ADD COLUMN notes TEXT")
            print("✓ notes added")
        else:
            print("✓ notes already exists")

        conn.commit()
        conn.close()
        print("✅ user_media planner columns migration completed")
        return True
    except Exception as e:
        print(f"❌ Error migrating user_media planner columns: {e}")
        return False

if __name__ == "__main__":
    print("🔄 Running migrations...")
    print("=" * 50)
    migrate_password_reset()
    migrate_user_media_planner_columns()
    print("Done.")
