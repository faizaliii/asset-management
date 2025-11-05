from flask import Flask
from .models import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///asset_manager.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key_here'

db.init_app(app)

with app.app_context():
    db.create_all()

# Import views (routes)
from . import views
