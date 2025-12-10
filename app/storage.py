"""
Storage service for barcode images.
Uses Railway volume storage for persistent file storage.
"""
import os
from barcode import Code128
from barcode.writer import ImageWriter

class BarcodeStorage:
    """Handles barcode image storage using Railway volumes"""
    
    def __init__(self, app=None):
        self.app = app
        self.storage_path = None
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize storage with app configuration"""
        self.app = app
        
        # Use Railway volume if available, otherwise use local static directory
        # Railway volumes are mounted at /data by default
        railway_volume = os.environ.get('RAILWAY_VOLUME_MOUNT_PATH', '/data')
        
        if os.path.exists(railway_volume):
            # Use Railway volume
            self.storage_path = os.path.join(railway_volume, 'barcodes')
            print(f"Using Railway volume storage at: {self.storage_path}")
        else:
            # Fall back to local static directory for development
            app_dir = os.path.dirname(os.path.abspath(__file__))
            self.storage_path = os.path.join(app_dir, 'static', 'barcodes')
            print(f"Using local storage at: {self.storage_path}")
        
        # Create directory if it doesn't exist
        os.makedirs(self.storage_path, exist_ok=True)
    
    def generate_and_store(self, serial_number):
        """
        Generate barcode and store it
        Returns the URL/path to the barcode image
        """
        try:
            # Generate barcode image
            code128 = Code128(serial_number, writer=ImageWriter())
            
            # Save to storage path
            barcode_path = os.path.join(self.storage_path, serial_number)
            code128.save(barcode_path)
            
            # Return relative URL for serving
            # In production, this will be served from /static/barcodes/
            return f"/static/barcodes/{serial_number}.png"
                
        except Exception as e:
            print(f"Barcode generation error: {str(e)}")
            return None
    
    def delete(self, serial_number_or_url):
        """
        Delete a barcode image
        Accepts either a serial number or a URL path
        """
        if not serial_number_or_url:
            return
        
        try:
            # Extract serial number from URL if needed
            if '/barcodes/' in str(serial_number_or_url):
                serial_number = str(serial_number_or_url).split('/barcodes/')[-1].replace('.png', '')
            else:
                serial_number = str(serial_number_or_url).replace('.png', '')
            
            # Delete from storage
            barcode_path = os.path.join(self.storage_path, f'{serial_number}.png')
            if os.path.exists(barcode_path):
                os.remove(barcode_path)
                print(f"Deleted barcode: {barcode_path}")
        except Exception as e:
            print(f"Delete error: {str(e)}")

# Create global storage instance
storage = BarcodeStorage()
