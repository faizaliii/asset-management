import sys
import os

# Get the script directory and parent directory
script_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(script_dir)  # This is the 'app' directory
parent_dir = os.path.dirname(app_dir)  # This is the project root directory

# Add parent directory to Python path so we can import 'app'
sys.path.insert(0, parent_dir)

# Change to parent directory (project root)
os.chdir(parent_dir)

from app import app
from app.models import db

# Drop and recreate all tables
with app.app_context():
    db.drop_all()
    db.create_all()
    print("Database recreated successfully!")

