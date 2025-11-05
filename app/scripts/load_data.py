import csv
import sys
import os

# Get the script directory and parent directory
script_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(script_dir)  # This is the 'app' directory
parent_dir = os.path.dirname(app_dir)  # This is the 'Asset Manager' directory

# Add parent directory to Python path so we can import 'app'
sys.path.insert(0, parent_dir)

# Change to app directory for CSV file paths
os.chdir(app_dir)

from app import app
from app.models import db, Location, SubLocation, Category, SubCategory


def load_locations(filepath='locations.csv'):
    with open(filepath, 'r') as file:
        reader = csv.DictReader(file)
        count = 0
        for row in reader:
            # Check if location already exists
            existing = Location.query.filter_by(code=row['code']).first()
            if not existing:
                location = Location(name=row['name'], code=row['code'])
                db.session.add(location)
                count += 1
        db.session.commit()
    print(f"Loaded {count} locations from {filepath}")


def load_sublocations(filepath='sublocations.csv'):
    with open(filepath, 'r') as file:
        reader = csv.DictReader(file)
        count = 0
        for row in reader:
            # Check if sublocation already exists
            existing = SubLocation.query.filter_by(code=row['code'], location_id=row['location_id']).first()
            if not existing:
                sublocation = SubLocation(name=row['name'], code=row['code'], location_id=row['location_id'])
                db.session.add(sublocation)
                count += 1
        db.session.commit()
    print(f"Loaded {count} sublocations from {filepath}")


def load_categories(filepath='categories.csv'):
    with open(filepath, 'r') as file:
        reader = csv.DictReader(file)
        count = 0
        for row in reader:
            # Check if category already exists
            existing = Category.query.filter_by(code=row['code']).first()
            if not existing:
                category = Category(name=row['name'], code=row['code'])
                db.session.add(category)
                count += 1
        db.session.commit()
    print(f"Loaded {count} categories from {filepath}")


def load_subcategories(filepath='subcategories.csv'):
    with open(filepath, 'r') as file:
        reader = csv.DictReader(file)
        count = 0
        for row in reader:
            # Check if subcategory already exists
            existing = SubCategory.query.filter_by(code=row['code'], category_id=row['category_id']).first()
            if not existing:
                subcategory = SubCategory(name=row['name'], code=row['code'], category_id=row['category_id'])
                db.session.add(subcategory)
                count += 1
        db.session.commit()
    print(f"Loaded {count} subcategories from {filepath}")


if __name__ == '__main__':
    with app.app_context():
        load_locations()
        load_sublocations()
        load_categories()
        load_subcategories()
