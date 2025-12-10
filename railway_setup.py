#!/usr/bin/env python3
"""
Railway setup script - Run this to initialize the database
Usage: railway run python railway_setup.py
"""
import sys
import os

# Ensure we're in the right directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
sys.path.insert(0, script_dir)

from app import app
from app.models import db, Location, SubLocation, Category, SubCategory, User
import csv

def init_db():
    """Initialize database"""
    print("Initializing database...")
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("✓ Database created successfully!")

def load_data():
    """Load initial data from CSV files"""
    print("\nLoading initial data...")
    with app.app_context():
        # Load locations
        count = 0
        csv_path = os.path.join(script_dir, 'app', 'locations.csv')
        if os.path.exists(csv_path):
            with open(csv_path, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    existing = Location.query.filter_by(code=row['code']).first()
                    if not existing:
                        location = Location(name=row['name'], code=row['code'])
                        db.session.add(location)
                        count += 1
            print(f"✓ Loaded {count} locations")
        
        # Load categories
        count = 0
        csv_path = os.path.join(script_dir, 'app', 'categories.csv')
        if os.path.exists(csv_path):
            with open(csv_path, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    existing = Category.query.filter_by(code=row['code']).first()
                    if not existing:
                        category = Category(name=row['name'], code=row['code'])
                        db.session.add(category)
                        count += 1
            print(f"✓ Loaded {count} categories")
        
        # Load sublocations
        count = 0
        csv_path = os.path.join(script_dir, 'app', 'sublocations.csv')
        if os.path.exists(csv_path):
            with open(csv_path, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    existing = SubLocation.query.filter_by(code=row['code']).first()
                    if not existing:
                        location = Location.query.filter_by(id=int(row['location_id'])).first()
                        if location:
                            sublocation = SubLocation(name=row['name'], code=row['code'], location_id=location.id)
                            db.session.add(sublocation)
                            count += 1
            print(f"✓ Loaded {count} sublocations")
        
        # Load subcategories
        count = 0
        csv_path = os.path.join(script_dir, 'app', 'subcategories.csv')
        if os.path.exists(csv_path):
            with open(csv_path, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    existing = SubCategory.query.filter_by(code=row['code']).first()
                    if not existing:
                        category = Category.query.filter_by(id=int(row['category_id'])).first()
                        if category:
                            subcategory = SubCategory(name=row['name'], code=row['code'], category_id=category.id)
                            db.session.add(subcategory)
                            count += 1
            print(f"✓ Loaded {count} subcategories")
        
        db.session.commit()

def create_users():
    """Create default users"""
    print("\nCreating users...")
    with app.app_context():
        users_to_create = [
            ('admin', 'admin123', 'admin'),
            ('user1', 'password1', 'member'),
            ('user2', 'password2', 'member'),
            ('manager', 'manager123', 'member'),
            ('staff', 'staff123', 'member'),
        ]
        
        created_count = 0
        for username, password, role in users_to_create:
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                print(f"  - User '{username}' already exists. Skipping...")
                continue
            
            user = User(username=username, role=role)
            user.set_password(password)
            db.session.add(user)
            created_count += 1
            print(f"  ✓ Created user: {username} (role: {role})")
        
        if created_count > 0:
            db.session.commit()
            print(f"\n✓ Successfully created {created_count} user(s).")
        else:
            print("\n✓ No new users created. All users already exist.")

if __name__ == '__main__':
    try:
        init_db()
        load_data()
        create_users()
        print("\n" + "="*50)
        print("Setup complete! Your application is ready.")
        print("="*50)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

