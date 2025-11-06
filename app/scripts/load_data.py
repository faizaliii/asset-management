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
        skipped = 0
        for row in reader:
            # Skip empty rows
            if not row.get('code') or not (row.get('location_code') or row.get('location_id')):
                skipped += 1
                continue
            
            # Look up location by code (preferred) or by ID (backward compatibility)
            if 'location_code' in row and row['location_code']:
                location = Location.query.filter_by(code=row['location_code']).first()
                if not location:
                    print(f"  Warning: Location with code '{row['location_code']}' not found. Skipping sublocation '{row['code']}'.")
                    skipped += 1
                    continue
                location_id = location.id
            else:
                # Backward compatibility: use location_id if provided
                location_id = int(row['location_id'])
            
            # Check if sublocation already exists
            existing = SubLocation.query.filter_by(code=row['code'], location_id=location_id).first()
            if not existing:
                sublocation = SubLocation(name=row['name'], code=row['code'], location_id=location_id)
                db.session.add(sublocation)
                count += 1
        db.session.commit()
    print(f"Loaded {count} sublocations from {filepath}" + (f" ({skipped} skipped)" if skipped > 0 else ""))


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
        skipped = 0
        for row in reader:
            # Skip empty rows
            if not row.get('code') or not (row.get('category_code') or row.get('category_id')):
                skipped += 1
                continue
            
            # Look up category by code (preferred) or by ID (backward compatibility)
            if 'category_code' in row and row['category_code']:
                category = Category.query.filter_by(code=row['category_code']).first()
                if not category:
                    print(f"  Warning: Category with code '{row['category_code']}' not found. Skipping subcategory '{row['code']}'.")
                    skipped += 1
                    continue
                category_id = category.id
            else:
                # Backward compatibility: use category_id if provided
                category_id = int(row['category_id'])
            
            # Check if subcategory already exists
            existing = SubCategory.query.filter_by(code=row['code'], category_id=category_id).first()
            if not existing:
                subcategory = SubCategory(name=row['name'], code=row['code'], category_id=category_id)
                db.session.add(subcategory)
                count += 1
        db.session.commit()
    print(f"Loaded {count} subcategories from {filepath}" + (f" ({skipped} skipped)" if skipped > 0 else ""))


if __name__ == '__main__':
    with app.app_context():
        load_locations()
        load_sublocations()
        load_categories()
        load_subcategories()
