# Asset Management System

A comprehensive asset management application built with Flask that allows you to register, track, and manage assets with barcode generation, maintenance scheduling, and movement tracking.

## Features

- **Asset Registration**: Register assets with serial number and barcode generation
- **Asset Tracking**: Track assets by location, category, subcategory, and status
- **Barcode Generation**: Automatic barcode generation for each asset
- **Maintenance Management**: Schedule and track maintenance/repairs
- **Movement History**: Track asset transfers between locations
- **Filtering**: Filter assets by multiple criteria
- **Reports**: Depreciation summaries and disposal reports

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- **Python 3.8+** (Python 3.11 or 3.13 recommended)
- **pip** (Python package installer)
- **Git** (optional, if cloning from repository)

## Installation Steps

### 1. Clone or Copy the Project

If you have the project in a repository:
```bash
git clone <repository-url>
cd asset-management
```

Or if you're copying the project files, navigate to the project directory:
```bash
cd /path/to/asset-management
```

### 2. Create Virtual Environment

Create a virtual environment to isolate project dependencies:

```bash
python3 -m venv venv
```

**On macOS/Linux:**
```bash
source venv/bin/activate
```

**On Windows:**
```bash
venv\Scripts\activate
```

### 3. Install Dependencies

Install all required Python packages:

```bash
pip install -r ../requirements.txt
```

Or install packages individually:
```bash
pip install Flask==3.1.2 Flask-SQLAlchemy==3.1.1 python-barcode==0.16.1 Pillow==12.0.0 Werkzeug==3.1.3
```

### 4. Initialize Database

Create the database tables:

```bash
python app/scripts/init_db.py
```

This will create a new SQLite database file (`asset_manager.db`) in the `instance/` directory.

### 5. Load Initial Data

Load locations, sublocations, categories, and subcategories from CSV files:

```bash
python app/scripts/load_data.py
```

This will populate the database with data from:
- `app/locations.csv`
- `app/sublocations.csv`
- `app/categories.csv`
- `app/subcategories.csv`

**Note:** You can edit these CSV files to customize your locations, categories, etc. The format should be:
- **locations.csv**: `name,code`
- **sublocations.csv**: `name,code,location_id`
- **categories.csv**: `name,code`
- **subcategories.csv**: `name,code,category_id`

### 6. Set Environment Variable

Set the Flask application environment variable:

**On macOS/Linux:**
```bash
export FLASK_APP=app
```

**On Windows:**
```bash
set FLASK_APP=app
```

### 7. Run the Application

Start the Flask development server:

```bash
flask run --port=5002
```

Or use the run.py file:
```bash
python run.py
```

The application will be available at: **http://127.0.0.1:5002**

### 8. Access the Application

Open your web browser and navigate to:
```
http://127.0.0.1:5002
```

## Project Structure

```
Asset Manager/
├── asset-management/
│   ├── app/
│   │   ├── __init__.py          # Flask app initialization
│   │   ├── models.py             # Database models
│   │   ├── views.py              # Routes and views
│   │   ├── templates/            # HTML templates
│   │   ├── static/
│   │   │   └── barcodes/         # Generated barcode images
│   │   ├── scripts/
│   │   │   ├── init_db.py        # Database initialization script
│   │   │   └── load_data.py      # Data loading script
│   │   ├── locations.csv         # Location data
│   │   ├── sublocations.csv      # Sublocation data
│   │   ├── categories.csv        # Category data
│   │   └── subcategories.csv    # Subcategory data
│   ├── instance/
│   │   └── asset_manager.db     # SQLite database
│   └── run.py                    # Application entry point
├── requirements.txt               # Python dependencies
└── README.md                     # This file
```

## Configuration

### Database Configuration

The application uses SQLite by default. The database file is stored in `instance/asset_manager.db`.

To change the database location, edit `app/__init__.py`:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'
```

### Secret Key

For production use, change the secret key in `app/__init__.py`:
```python
app.secret_key = 'your-unique-secret-key-here'
```

## Usage

### Registering an Asset

1. Navigate to the asset list page
2. Click "Register New Asset"
3. Fill in all required fields:
   - Name
   - Type
   - Category and SubCategory
   - Location and SubLocation
   - Status
   - Depreciation percentage
   - Purchase date
4. Click "Register"

The system will automatically:
- Generate a unique serial number (format: `LOCATION_CODE-CATEGORY_CODE-SUBLOCATION_CODE-001`)
- Create a barcode image
- Save the asset to the database

### Managing Assets

- **View Assets**: Browse all assets with filtering options
- **Edit Asset**: Change name, type, and status (limited fields)
- **Move Asset**: Transfer assets between locations (updates serial number)
- **Schedule Maintenance**: Add maintenance records
- **View History**: Check maintenance history and movement history

### Filtering Assets

Use the filter dropdowns on the asset list page to filter by:
- Status (Active, Under Repair, Disposed)
- Location
- SubLocation
- Category
- SubCategory

## Troubleshooting

### Port Already in Use

If port 5002 is already in use, you can:

1. **Kill the process using the port:**
   ```bash
   lsof -ti:5002 | xargs kill -9
   ```

2. **Use a different port:**
   ```bash
   flask run --port=5003
   ```

### Database Errors

If you encounter database errors:

1. **Delete the existing database:**
   ```bash
   rm instance/asset_manager.db
   ```

2. **Reinitialize the database:**
   ```bash
   python app/scripts/init_db.py
   python app/scripts/load_data.py
   ```

### Barcode Not Showing

If barcodes are not displaying:

1. **Regenerate barcode** using the "Regenerate" button on the asset detail page
2. **Check file permissions** on the `app/static/barcodes/` directory
3. **Ensure Pillow is installed:** `pip install Pillow`

### Import Errors

If you get import errors:

1. **Ensure virtual environment is activated**
2. **Reinstall dependencies:** `pip install -r ../requirements.txt`
3. **Check Python version:** `python --version` (should be 3.8+)

## Development

### Running in Debug Mode

For development with auto-reload:

```bash
export FLASK_APP=app
export FLASK_ENV=development
flask run --port=5002
```

Or edit `run.py` to set `debug=True`.

## Production Deployment

For production deployment on shared hosting (like Hostinger or GoDaddy):

1. **Use a production WSGI server** like Gunicorn:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5002 app:app
   ```

2. **Change secret key** to a secure random string
3. **Set up proper file permissions** for the database and static directories
4. **Configure static file serving** through your web server

## Common Commands

```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Run application
flask run --port=5002

# Initialize database
python app/scripts/init_db.py

# Load data
python app/scripts/load_data.py

# Deactivate virtual environment
deactivate
```

## Support

For issues or questions, check:
- Flask documentation: https://flask.palletsprojects.com/
- SQLAlchemy documentation: https://www.sqlalchemy.org/
- Python Barcode documentation: https://python-barcode.readthedocs.io/

## License

This project is provided as-is for internal use.

