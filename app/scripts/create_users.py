"""
Script to manually create users in the database.
Run this script to create initial users for the system.

Usage:
    python app/scripts/create_users.py
"""

import sys
import os

# Add parent directory to path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, parent_dir)
os.chdir(parent_dir)

from app import app
from app.models import db, User

def create_users():
    """Create default users"""
    with app.app_context():
        # List of users to create (username, password, role)
        # role: 'admin' or 'member'
        users_to_create = [
            ('admin', 'admin123', 'admin'),
            ('user1', 'password1', 'member'),
            ('user2', 'password2', 'member'),
            ('manager', 'manager123', 'member'),
            ('staff', 'staff123', 'member'),
        ]
        
        created_count = 0
        for username, password, role in users_to_create:
            # Check if user already exists
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                print(f"User '{username}' already exists. Skipping...")
                continue
            
            # Create new user
            user = User(username=username, role=role)
            user.set_password(password)
            db.session.add(user)
            created_count += 1
            print(f"Created user: {username} (role: {role})")
        
        if created_count > 0:
            db.session.commit()
            print(f"\nSuccessfully created {created_count} user(s).")
        else:
            print("\nNo new users created. All users already exist.")
        
        # Display all users
        print("\nAll users in database:")
        all_users = User.query.all()
        for user in all_users:
            print(f"  - {user.username} (ID: {user.id}, Role: {user.role})")

if __name__ == '__main__':
    create_users()

