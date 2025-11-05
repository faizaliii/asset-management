from flask import render_template, request, redirect, url_for, flash, current_app
from . import app
from .models import db, Asset, Location, SubLocation, Category, SubCategory, AssetMovement, Maintenance, Disposal
from sqlalchemy.exc import IntegrityError
import os
from datetime import date

from barcode import Code128
from barcode.writer import ImageWriter

# Modify the default route to redirect to 'list_assets'
@app.route('/')
def home():
    return redirect(url_for('list_assets'))

@app.route('/locations', methods=['GET', 'POST'])
def manage_locations():
    if request.method == 'POST':
        # Add new location
        pass
    locations = Location.query.all()
    return render_template('locations.html', locations=locations)

@app.route('/categories', methods=['GET', 'POST'])
def manage_categories():
    if request.method == 'POST':
        # Add new category
        pass
    categories = Category.query.all()
    return render_template('categories.html', categories=categories)

@app.route('/subcategories', methods=['GET', 'POST'])
def manage_subcategories():
    if request.method == 'POST':
        # Add new subcategory
        pass
    subcategories = SubCategory.query.all()
    return render_template('subcategories.html', subcategories=subcategories)

# Enhance asset registration
@app.route('/register', methods=['GET', 'POST'])
def register_asset():
    if request.method == 'POST':
        try:
            name = request.form['name']
            asset_type = request.form['type']
            category_id = int(request.form['category'])
            subcategory_id = int(request.form['subcategory'])
            location_id = int(request.form['location'])
            sublocation_id = int(request.form['sublocation'])
            status = request.form['status']
            depreciation = float(request.form['depreciation'])
            purchased_on = date.fromisoformat(request.form['purchased_on'])

            # Generate Serial Number
            location_obj = Location.query.get(location_id)
            category_obj = Category.query.get(category_id)
            sublocation_obj = SubLocation.query.get(sublocation_id)
            
            if not location_obj or not category_obj or not sublocation_obj:
                flash('Invalid location, category, or sublocation selected!')
                categories = Category.query.all()
                subcategories = SubCategory.query.all()
                locations = Location.query.all()
                sublocations = SubLocation.query.all()
                return render_template('register_asset.html', categories=categories, subcategories=subcategories, locations=locations, sublocations=sublocations)
            
            location_code = location_obj.code
            category_code = category_obj.code
            sublocation_code = sublocation_obj.code
            
            existing_assets = Asset.query.filter_by(
                category_id=category_id,
                subcategory_id=subcategory_id
            ).count()
            serial_suffix = str(existing_assets + 1).zfill(3)
            serial_number = f"{location_code}-{category_code}-{sublocation_code}-{serial_suffix}"

            # Generate Barcode
            try:
                # Get the directory where this file is located
                app_dir = os.path.dirname(os.path.abspath(__file__))
                barcode_dir = os.path.join(app_dir, 'static', 'barcodes')
                os.makedirs(barcode_dir, exist_ok=True)
                # Save without extension - the library will add it
                barcode_path = os.path.join(barcode_dir, serial_number)
                code128 = Code128(serial_number, writer=ImageWriter())
                code128.save(barcode_path)
            except Exception as barcode_error:
                # Log barcode error but don't fail asset creation
                print(f"Barcode generation error: {str(barcode_error)}")
                # Continue without barcode for now
                pass

            # Create new Asset
            new_asset = Asset(
                name=name,
                type=asset_type,
                category_id=category_id,
                subcategory_id=subcategory_id,
                location_id=location_id,
                sublocation_id=sublocation_id,
                status=status,
                depreciation=depreciation,
                purchased_on=purchased_on,
                serial_number=serial_number
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
def asset_detail(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    locations = Location.query.all()
    sublocations = SubLocation.query.all()
    return render_template('asset_detail.html', asset=asset, locations=locations, sublocations=sublocations)

@app.route('/edit_asset/<int:asset_id>', methods=['GET', 'POST'])
def edit_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    if request.method == 'POST':
        asset.name = request.form['name']
        asset.type = request.form['type']
        asset.status = request.form['status']

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
def move_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    new_location_id = int(request.form['new_location'])
    new_sublocation_id = int(request.form['new_sublocation'])
    
    old_location_id = asset.location_id
    location_changed = old_location_id != new_location_id

    if asset.location_id != new_location_id or asset.sublocation_id != new_sublocation_id:
        # Record movement
        movement = AssetMovement(
            asset_id=asset.id,
            from_location_id=asset.location_id,
            to_location_id=new_location_id,
            movement_date=date.today()
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
                
                # Get the new location, category, and sublocation codes
                location_obj = Location.query.get(new_location_id)
                category_obj = Category.query.get(asset.category_id)
                sublocation_obj = SubLocation.query.get(new_sublocation_id)
                
                location_code = location_obj.code
                category_code = category_obj.code
                sublocation_code = sublocation_obj.code
                
                # Keep the same sequential number (last part of serial number)
                # Extract the current sequential number from existing serial
                old_serial_parts = old_serial_number.split('-')
                serial_suffix = old_serial_parts[-1] if len(old_serial_parts) > 0 else "001"
                
                # Generate new serial number with new location code
                new_serial_number = f"{location_code}-{category_code}-{sublocation_code}-{serial_suffix}"
                
                # Update serial number
                asset.serial_number = new_serial_number
                
                # Regenerate barcode
                app_dir = os.path.dirname(os.path.abspath(__file__))
                barcode_dir = os.path.join(app_dir, 'static', 'barcodes')
                os.makedirs(barcode_dir, exist_ok=True)
                
                # Remove old barcode if exists
                old_barcode_path = os.path.join(barcode_dir, f'{old_serial_number}.png')
                if os.path.exists(old_barcode_path):
                    os.remove(old_barcode_path)
                
                # Generate new barcode
                barcode_path = os.path.join(barcode_dir, new_serial_number)
                code128 = Code128(new_serial_number, writer=ImageWriter())
                code128.save(barcode_path)
                
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
def maintenance_history(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    maintenance_records = Maintenance.query.filter_by(asset_id=asset_id).all()
    return render_template('maintenance_history.html', asset=asset, maintenance_records=maintenance_records)

@app.route('/regenerate_barcode/<int:asset_id>', methods=['GET'])
def regenerate_barcode(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    try:
        # Get the directory where this file is located
        app_dir = os.path.dirname(os.path.abspath(__file__))
        barcode_dir = os.path.join(app_dir, 'static', 'barcodes')
        os.makedirs(barcode_dir, exist_ok=True)
        
        # Generate barcode
        barcode_path = os.path.join(barcode_dir, asset.serial_number)
        code128 = Code128(asset.serial_number, writer=ImageWriter())
        code128.save(barcode_path)
        
        flash('Barcode regenerated successfully!', 'success')
    except Exception as e:
        flash(f'Error regenerating barcode: {str(e)}', 'error')
    
    return redirect(url_for('asset_detail', asset_id=asset_id))

@app.route('/depreciation_summary', methods=['GET'])
def depreciation_summary():
    assets = Asset.query.all()
    depreciation_data = []

    for asset in assets:
        age_in_years = (date.today() - asset.purchased_on).days / 365.25
        depreciation_value = asset.depreciation * age_in_years
        book_value = max(asset.purchase_price - depreciation_value, 0)
        depreciation_data.append({
            'asset': asset,
            'depreciation_value': depreciation_value,
            'book_value': book_value
        })

    return render_template('depreciation_summary.html', depreciation_data=depreciation_data)

@app.route('/disposal_report', methods=['GET'])
def disposal_report():
    disposed_assets = Asset.query.filter_by(status='Disposed').all()
    return render_template('disposal_report.html', disposed_assets=disposed_assets)
