#!/bin/bash
# Railway setup script
# Run this after deployment to initialize the database

echo "Initializing database..."
railway run python app/scripts/init_db.py

echo "Loading initial data..."
railway run python app/scripts/load_data.py

echo "Creating users..."
railway run python app/scripts/create_users.py

echo "Setup complete!"

