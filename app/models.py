from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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
    type = db.Column(db.String(50), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    subcategory_id = db.Column(db.Integer, db.ForeignKey('sub_category.id'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    sublocation_id = db.Column(db.Integer, db.ForeignKey('sub_location.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    assigned_to = db.Column(db.String(100))
    depreciation = db.Column(db.Float, nullable=False)
    purchased_on = db.Column(db.Date, nullable=False)
    serial_number = db.Column(db.String(100), unique=True, nullable=False)
    
    # Relationships
    category = db.relationship('Category', backref='assets')
    subcategory = db.relationship('SubCategory', backref='assets')
    location = db.relationship('Location', backref='assets')
    sub_location = db.relationship('SubLocation', backref='assets')

class AssetMovement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'), nullable=False)
    from_location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    to_location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    movement_date = db.Column(db.Date, nullable=False)

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
