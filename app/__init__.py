from flask import Flask
from .models import db
import os

app = Flask(__name__)

# Database configuration
database_url = os.environ.get('DATABASE_URL', 'sqlite:///asset_manager.db')
# Railway uses postgres:// but SQLAlchemy expects postgresql://
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key_here_change_in_production')

db.init_app(app)

with app.app_context():
    db.create_all()

# Initialize storage service
from .storage import storage
storage.init_app(app)

# Add route to serve barcode images from Railway volume
@app.route('/static/barcodes/<path:filename>')
def serve_barcode(filename):
    """Serve barcode images from storage (Railway volume or local)"""
    from .storage import storage
    storage_dir = storage.storage_path
    return send_from_directory(storage_dir, filename)

# Import views (routes)
from . import views
