from flask_sqlalchemy import SQLAlchemy
from datetime import date
from dateutil.relativedelta import relativedelta
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='member')  # 'admin' or 'member'
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if user is an admin"""
        return self.role == 'admin'

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    code = db.Column(db.String(10), unique=True, nullable=False)

class SubLocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    code = db.Column(db.String(10), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    code = db.Column(db.String(10), unique=True, nullable=False)

class SubCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    code = db.Column(db.String(10), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    subcategory_id = db.Column(db.Integer, db.ForeignKey('sub_category.id'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    sublocation_id = db.Column(db.Integer, db.ForeignKey('sub_location.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    assigned_to = db.Column(db.String(100))
    purchased_on = db.Column(db.Date, nullable=False)
    serial_number = db.Column(db.String(100), unique=True, nullable=False)
    unit_of_measure = db.Column(db.String(10), default='number')  # ft., sqft., number, tr.
    quantity = db.Column(db.Float, default=1.0)
    
    # Relationships
    category = db.relationship('Category', backref='assets')
    subcategory = db.relationship('SubCategory', backref='assets')
    location = db.relationship('Location', backref='assets')
    sub_location = db.relationship('SubLocation', backref='assets')
    
    @property
    def age(self):
        """Calculate age from purchase date in format: X years Y months"""
        if not self.purchased_on:
            return "N/A"
        delta = relativedelta(date.today(), self.purchased_on)
        years = delta.years
        months = delta.months
        if years == 0 and months == 0:
            return "Less than 1 month"
        elif years == 0:
            return f"{months} month{'s' if months != 1 else ''}"
        elif months == 0:
            return f"{years} year{'s' if years != 1 else ''}"
        else:
            return f"{years} year{'s' if years != 1 else ''} and {months} month{'s' if months != 1 else ''}"

class AssetMovement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'), nullable=False)
    from_location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    from_sublocation_id = db.Column(db.Integer, db.ForeignKey('sub_location.id'))
    to_location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    to_sublocation_id = db.Column(db.Integer, db.ForeignKey('sub_location.id'))
    movement_date = db.Column(db.Date, nullable=False)
    moved_by = db.Column(db.String(100))  # User who moved the asset
    
    # Relationships
    asset = db.relationship('Asset', backref='movements')
    from_location = db.relationship('Location', foreign_keys=[from_location_id], backref='from_movements')
    to_location = db.relationship('Location', foreign_keys=[to_location_id], backref='to_movements')
    from_sublocation = db.relationship('SubLocation', foreign_keys=[from_sublocation_id], backref='from_movements')
    to_sublocation = db.relationship('SubLocation', foreign_keys=[to_sublocation_id], backref='to_movements')

class AssetHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'), nullable=False)
    field_name = db.Column(db.String(50), nullable=False)
    old_value = db.Column(db.String(200))
    new_value = db.Column(db.String(200))
    updated_by = db.Column(db.String(100))
    updated_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    
    # Relationships
    asset = db.relationship('Asset', backref='history')

class Maintenance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))

class Disposal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'), nullable=False)
    disposal_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.String(200))
