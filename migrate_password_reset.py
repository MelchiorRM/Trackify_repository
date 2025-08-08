#!/usr/bin/env python3
"""
Database migration script to add password reset functionality
This script adds reset_token and reset_token_expiry columns to the users table
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

if __name__ == "__main__":
    print("🔄 Starting password reset migration...")
    print("=" * 50)
    
    success = migrate_password_reset()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("You can now use the password reset functionality.")
    else:
        print("\n💥 Migration failed!")
        print("Please check the error messages above and try again.")
