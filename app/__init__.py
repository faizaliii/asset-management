from flask import Flask, send_from_directory
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
    # Only create tables if they don't exist - migration endpoint handles schema updates
    db.create_all()

# Initialize storage service
from .storage import storage
storage.init_app(app)

# Add route to serve barcode images from Railway volume
@app.route('/static/barcodes/<path:filename>')
def serve_barcode(filename):
    """Serve barcode images from storage (Railway volume or local)"""
    try:
        from .storage import storage
        storage_dir = storage.storage_path
        return send_from_directory(storage_dir, filename)
    except Exception as e:
        # Return 404 if file not found instead of crashing
        from flask import abort
        abort(404)

# Import views (routes)
from . import views
