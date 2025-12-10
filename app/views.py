from flask import render_template, request, redirect, url_for, flash, current_app, session, send_from_directory
from functools import wraps
from . import app
from .models import db, Asset, Location, SubLocation, Category, SubCategory, AssetMovement, Maintenance, Disposal, AssetHistory, User
from .storage import storage
from sqlalchemy.exc import IntegrityError
import os
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'error')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'error')
            return redirect(url_for('login', next=request.url))
        
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin():
            flash('You do not have permission to perform this action. Admin access required.', 'error')
            return redirect(url_for('list_assets'))
        
        return f(*args, **kwargs)
    return decorated_function

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please enter both username and password.', 'error')
            return render_template('login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash(f'Welcome back, {user.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('list_assets'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not username or not password:
            flash('Please enter both username and password.', 'error')
            return render_template('signup.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('signup.html')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose another.', 'error')
            return render_template('signup.html')
        
        user = User(username=username, role='member')  # Default role is 'member'
        user.set_password(password)
        db.session.add(user)
        try:
            db.session.commit()
            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating account: {str(e)}', 'error')
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

# Modify the default route to redirect to 'list_assets'
@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('list_assets'))

@app.route('/locations', methods=['GET', 'POST'])
@admin_required
def manage_locations():
    if request.method == 'POST':
        # Add new location
        pass
    locations = Location.query.all()
    return render_template('locations.html', locations=locations)

@app.route('/categories', methods=['GET', 'POST'])
@admin_required
def manage_categories():
    if request.method == 'POST':
        # Add new category
        pass
    categories = Category.query.all()
    return render_template('categories.html', categories=categories)

@app.route('/subcategories', methods=['GET', 'POST'])
@admin_required
def manage_subcategories():
    if request.method == 'POST':
        # Add new subcategory
        pass
    subcategories = SubCategory.query.all()
    return render_template('subcategories.html', subcategories=subcategories)

# Enhance asset registration
@app.route('/register', methods=['GET', 'POST'])
@admin_required
def register_asset():
    if request.method == 'POST':
        try:
            name = request.form['name']
            category_id = int(request.form['category'])
            subcategory_id = int(request.form['subcategory'])
            location_id = int(request.form['location'])
            sublocation_id = int(request.form['sublocation'])
            status = request.form['status']
            purchased_on = date.fromisoformat(request.form['purchased_on'])
            assigned_to = request.form.get('assigned_to', '')
            unit_of_measure = request.form.get('unit_of_measure', 'number')
            quantity = float(request.form.get('quantity', 1.0))

            # Generate Serial Number
            location_obj = Location.query.get(location_id)
            category_obj = Category.query.get(category_id)
            subcategory_obj = SubCategory.query.get(subcategory_id)
            
            if not location_obj or not category_obj or not subcategory_obj:
                flash('Invalid location, category, or subcategory selected!', 'error')
                categories = Category.query.all()
                subcategories = SubCategory.query.all()
                locations = Location.query.all()
                sublocations = SubLocation.query.all()
                return render_template('register_asset.html', categories=categories, subcategories=subcategories, locations=locations, sublocations=sublocations)
            
            location_code = location_obj.code
            category_code = category_obj.code
            subcategory_code = subcategory_obj.code
            
            existing_assets = Asset.query.filter_by(
                category_id=category_id,
                subcategory_id=subcategory_id
            ).count()
            serial_suffix = str(existing_assets + 1).zfill(5)  # 5 digits instead of 3
            serial_number = f"{location_code}-{category_code}-{subcategory_code}-{serial_suffix}"

            # Generate and store barcode
            barcode_url = storage.generate_and_store(serial_number)

            # Create new Asset
            new_asset = Asset(
                name=name,
                category_id=category_id,
                subcategory_id=subcategory_id,
                location_id=location_id,
                sublocation_id=sublocation_id,
                status=status,
                purchased_on=purchased_on,
                serial_number=serial_number,
                barcode_url=barcode_url,
                assigned_to=assigned_to,
                unit_of_measure=unit_of_measure,
                quantity=quantity
            )
            db.session.add(new_asset)
            db.session.commit()
            flash('Asset registered successfully!', 'success')
            return redirect(url_for('list_assets'))
        except IntegrityError:
            db.session.rollback()
            flash('Asset with the same serial number exists!', 'error')
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating asset: {str(e)}', 'error')

    categories = Category.query.all()
    subcategories = SubCategory.query.all()
    locations = Location.query.all()
    sublocations = SubLocation.query.all()
    return render_template('register_asset.html', categories=categories, subcategories=subcategories, locations=locations, sublocations=sublocations)

@app.route('/assets/<int:asset_id>', methods=['GET'])
@login_required
def asset_detail(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    locations = Location.query.all()
    sublocations = SubLocation.query.all()
    history = AssetHistory.query.filter_by(asset_id=asset_id).order_by(AssetHistory.updated_at.desc()).all()
    movements = AssetMovement.query.filter_by(asset_id=asset_id).order_by(AssetMovement.movement_date.desc()).all()
    return render_template('asset_detail.html', asset=asset, locations=locations, sublocations=sublocations, history=history, movements=movements)

@app.route('/edit_asset/<int:asset_id>', methods=['GET', 'POST'])
@admin_required
def edit_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    if request.method == 'POST':
        old_values = {
            'name': asset.name,
            'status': asset.status,
            'assigned_to': asset.assigned_to or '',
            'unit_of_measure': asset.unit_of_measure or 'number',
            'quantity': asset.quantity or 1.0
        }
        
        asset.name = request.form['name']
        asset.status = request.form['status']
        asset.assigned_to = request.form.get('assigned_to', '')
        asset.unit_of_measure = request.form.get('unit_of_measure', 'number')
        asset.quantity = float(request.form.get('quantity', 1.0))
        updated_by = session.get('username', 'System')
        
        # Track changes
        for field, old_value in old_values.items():
            new_value = getattr(asset, field) or ''
            if str(old_value) != str(new_value):
                history = AssetHistory(
                    asset_id=asset.id,
                    field_name=field,
                    old_value=str(old_value),
                    new_value=str(new_value),
                    updated_by=updated_by,
                    updated_at=datetime.now()
                )
                db.session.add(history)

        try:
            db.session.commit()
            flash('Asset updated successfully!', 'success')
            return redirect(url_for('list_assets'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating asset: {str(e)}', 'error')

    categories = Category.query.all()
    subcategories = SubCategory.query.all()
    locations = Location.query.all()
    sublocations = SubLocation.query.all()
    return render_template('edit_asset.html', asset=asset, categories=categories, subcategories=subcategories, locations=locations, sublocations=sublocations)

@app.route('/assets', methods=['GET'])
@login_required
def list_assets():
    status_filter = request.args.get('status')
    location_filter = request.args.get('location')
    sublocation_filter = request.args.get('sublocation')
    category_filter = request.args.get('category')
    subcategory_filter = request.args.get('subcategory')

    query = Asset.query

    if status_filter:
        query = query.filter_by(status=status_filter)
    if location_filter:
        query = query.filter_by(location_id=location_filter)
    if sublocation_filter:
        query = query.filter_by(sublocation_id=sublocation_filter)
    if category_filter:
        query = query.filter_by(category_id=category_filter)
    if subcategory_filter:
        query = query.filter_by(subcategory_id=subcategory_filter)

    assets = query.all()
    categories = Category.query.all()
    subcategories = SubCategory.query.all()
    locations = Location.query.all()
    sublocations = SubLocation.query.all()

    return render_template('assets_list.html', assets=assets, categories=categories, subcategories=subcategories, locations=locations, sublocations=sublocations)

@app.route('/move_asset/<int:asset_id>', methods=['POST'])
@admin_required
def move_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    new_location_id = int(request.form['new_location'])
    new_sublocation_id = int(request.form['new_sublocation'])
    moved_by = session.get('username', 'System')
    
    old_location_id = asset.location_id
    old_sublocation_id = asset.sublocation_id
    location_changed = old_location_id != new_location_id

    if asset.location_id != new_location_id or asset.sublocation_id != new_sublocation_id:
        # Record movement
        movement = AssetMovement(
            asset_id=asset.id,
            from_location_id=asset.location_id,
            from_sublocation_id=asset.sublocation_id,
            to_location_id=new_location_id,
            to_sublocation_id=new_sublocation_id,
            movement_date=date.today(),
            moved_by=moved_by
        )
        db.session.add(movement)
        
        # Update location and sublocation
        asset.location_id = new_location_id
        asset.sublocation_id = new_sublocation_id
        
        # If location changed, update serial number and regenerate barcode
        if location_changed:
            try:
                # Save old serial number for barcode deletion
                old_serial_number = asset.serial_number
                
                # Get the new location, category, and subcategory codes (using subcategory, not sublocation)
                location_obj = Location.query.get(new_location_id)
                category_obj = Category.query.get(asset.category_id)
                subcategory_obj = SubCategory.query.get(asset.subcategory_id)
                
                location_code = location_obj.code
                category_code = category_obj.code
                subcategory_code = subcategory_obj.code
                
                # Keep the same sequential number (last part of serial number)
                # Extract the current sequential number from existing serial
                old_serial_parts = old_serial_number.split('-')
                serial_suffix = old_serial_parts[-1] if len(old_serial_parts) > 0 else "00001"
                # Ensure it's 5 digits
                try:
                    serial_suffix = str(int(serial_suffix)).zfill(5)
                except ValueError:
                    serial_suffix = "00001"
                
                # Generate new serial number with new location code (using subcategory)
                new_serial_number = f"{location_code}-{category_code}-{subcategory_code}-{serial_suffix}"
                
                # Update serial number
                asset.serial_number = new_serial_number
                
                # Track serial number change in history
                history = AssetHistory(
                    asset_id=asset.id,
                    field_name='serial_number',
                    old_value=old_serial_number,
                    new_value=new_serial_number,
                    updated_by=session.get('username', 'System'),
                    updated_at=datetime.now()
                )
                db.session.add(history)
                
                # Delete old barcode
                if asset.barcode_url:
                    storage.delete(asset.barcode_url)
                
                # Generate and store new barcode
                new_barcode_url = storage.generate_and_store(new_serial_number)
                asset.barcode_url = new_barcode_url
                
            except Exception as barcode_error:
                print(f"Barcode generation error: {str(barcode_error)}")
                # Continue without barcode update for now
        
        db.session.commit()
        flash('Asset moved successfully!', 'success')
        if location_changed:
            flash('Serial number and barcode updated due to location change.', 'info')
    else:
        flash('No changes detected.', 'info')

    return redirect(url_for('asset_detail', asset_id=asset_id))

@app.route('/schedule_maintenance', methods=['POST'])
@admin_required
def schedule_maintenance():
    try:
        asset_id = int(request.form['asset_id'])
        start_date = date.fromisoformat(request.form['start_date'])
        end_date_str = request.form.get('end_date', '')
        end_date = date.fromisoformat(end_date_str) if end_date_str else None
        maintenance_type = request.form['type']
        description = request.form.get('description', '')

        maintenance = Maintenance(
            asset_id=asset_id,
            start_date=start_date,
            end_date=end_date,
            type=maintenance_type,
            description=description
        )
        db.session.add(maintenance)
        db.session.commit()

        flash('Maintenance scheduled successfully!', 'success')
        return redirect(url_for('asset_detail', asset_id=asset_id))
    except Exception as e:
        db.session.rollback()
        flash(f'Error scheduling maintenance: {str(e)}', 'error')
        return redirect(url_for('asset_detail', asset_id=int(request.form.get('asset_id', 0))))

@app.route('/maintenance_history/<int:asset_id>', methods=['GET'])
@login_required
def maintenance_history(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    maintenance_records = Maintenance.query.filter_by(asset_id=asset_id).all()
    return render_template('maintenance_history.html', asset=asset, maintenance_records=maintenance_records)

@app.route('/regenerate_barcode/<int:asset_id>', methods=['GET'])
@admin_required
def regenerate_barcode(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    try:
        # Delete old barcode if exists
        if asset.barcode_url:
            storage.delete(asset.barcode_url)
        
        # Generate and store new barcode
        new_barcode_url = storage.generate_and_store(asset.serial_number)
        asset.barcode_url = new_barcode_url
        db.session.commit()
        
        flash('Barcode regenerated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error regenerating barcode: {str(e)}', 'error')
    
    return redirect(url_for('asset_detail', asset_id=asset_id))

@app.route('/print_barcode/<int:asset_id>', methods=['GET'])
@login_required
def print_barcode(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    return render_template('print_barcode.html', asset=asset)

@app.route('/depreciation_summary', methods=['GET'])
@login_required
def depreciation_summary():
    # Depreciation summary removed as depreciation field was removed
    assets = Asset.query.all()
    return render_template('depreciation_summary.html', assets=assets)

@app.route('/disposal_report', methods=['GET'])
@login_required
def disposal_report():
    disposed_assets = Asset.query.filter_by(status='Disposed').all()
    return render_template('disposal_report.html', disposed_assets=disposed_assets)

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    """One-time setup endpoint - initialize database and load data"""
    import csv
    from .models import Location, SubLocation, Category, SubCategory, User
    
    # Simple security - check for setup token or allow only if no users exist
    setup_token = request.args.get('token') or request.form.get('token')
    expected_token = os.environ.get('SETUP_TOKEN', 'setup123')
    
    if setup_token != expected_token:
        return "Invalid setup token. Set SETUP_TOKEN environment variable.", 403
    
    try:
        # Drop and recreate all tables to ensure schema is up to date
        db.drop_all()
        db.create_all()
        
        # Load locations
        locations_file = os.path.join(os.path.dirname(__file__), 'locations.csv')
        if os.path.exists(locations_file):
            with open(locations_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if not Location.query.filter_by(code=row['code']).first():
                        db.session.add(Location(name=row['name'], code=row['code']))
        
        # Load categories
        categories_file = os.path.join(os.path.dirname(__file__), 'categories.csv')
        if os.path.exists(categories_file):
            with open(categories_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if not Category.query.filter_by(code=row['code']).first():
                        db.session.add(Category(name=row['name'], code=row['code']))
        
        # Load sublocations
        sublocations_file = os.path.join(os.path.dirname(__file__), 'sublocations.csv')
        if os.path.exists(sublocations_file):
            with open(sublocations_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if not SubLocation.query.filter_by(code=row['code']).first():
                        location = Location.query.filter_by(id=int(row['location_id'])).first()
                        if location:
                            db.session.add(SubLocation(name=row['name'], code=row['code'], location_id=location.id))
        
        # Load subcategories
        subcategories_file = os.path.join(os.path.dirname(__file__), 'subcategories.csv')
        if os.path.exists(subcategories_file):
            with open(subcategories_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if not SubCategory.query.filter_by(code=row['code']).first():
                        category = Category.query.filter_by(id=int(row['category_id'])).first()
                        if category:
                            db.session.add(SubCategory(name=row['name'], code=row['code'], category_id=category.id))
        
        # Create users
        users_data = [
            ('admin', 'admin123', 'admin'),
            ('user1', 'password1', 'member'),
            ('user2', 'password2', 'member'),
            ('manager', 'manager123', 'member'),
            ('staff', 'staff123', 'member'),
        ]
        
        for username, password, role in users_data:
            if not User.query.filter_by(username=username).first():
                user = User(username=username, role=role)
                user.set_password(password)
                db.session.add(user)
        
        db.session.commit()
        
        return """
        <h1>Setup Complete!</h1>
        <p>Database initialized successfully.</p>
        <p>Default users created:</p>
        <ul>
            <li>admin / admin123 (Admin)</li>
            <li>user1 / password1 (Member)</li>
            <li>user2 / password2 (Member)</li>
            <li>manager / manager123 (Member)</li>
            <li>staff / staff123 (Member)</li>
        </ul>
        <p><a href="/login">Go to Login</a></p>
        """
    except Exception as e:
        return f"Error during setup: {str(e)}", 500

@app.route('/migrate', methods=['GET'])
def migrate():
    """Migration endpoint - recreate tables with updated schema"""
    setup_token = request.args.get('token', '')
    expected_token = os.environ.get('SETUP_TOKEN', 'setup123')
    
    if setup_token != expected_token:
        return "Invalid setup token.", 403
    
    try:
        # Drop and recreate all tables to match current models
        db.drop_all()
        db.create_all()
        
        # Reload data
        import csv
        from .models import Location, SubLocation, Category, SubCategory, User
        
        # Load locations
        locations_file = os.path.join(os.path.dirname(__file__), 'locations.csv')
        if os.path.exists(locations_file):
            with open(locations_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    db.session.add(Location(name=row['name'], code=row['code']))
        
        # Load categories
        categories_file = os.path.join(os.path.dirname(__file__), 'categories.csv')
        if os.path.exists(categories_file):
            with open(categories_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    db.session.add(Category(name=row['name'], code=row['code']))
        
        # Load sublocations
        sublocations_file = os.path.join(os.path.dirname(__file__), 'sublocations.csv')
        if os.path.exists(sublocations_file):
            with open(sublocations_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    location = Location.query.filter_by(id=int(row['location_id'])).first()
                    if location:
                        db.session.add(SubLocation(name=row['name'], code=row['code'], location_id=location.id))
        
        # Load subcategories
        subcategories_file = os.path.join(os.path.dirname(__file__), 'subcategories.csv')
        if os.path.exists(subcategories_file):
            with open(subcategories_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    category = Category.query.filter_by(id=int(row['category_id'])).first()
                    if category:
                        db.session.add(SubCategory(name=row['name'], code=row['code'], category_id=category.id))
        
        # Recreate users
        users_data = [
            ('admin', 'admin123', 'admin'),
            ('user1', 'password1', 'member'),
            ('user2', 'password2', 'member'),
            ('manager', 'manager123', 'member'),
            ('staff', 'staff123', 'member'),
        ]
        
        for username, password, role in users_data:
            user = User(username=username, role=role)
            user.set_password(password)
            db.session.add(user)
        
        db.session.commit()
        
        return "Migration successful: Database recreated with updated schema. <a href='/login'>Go to Login</a>"
    except Exception as e:
        return f"Migration error: {str(e)}", 500
