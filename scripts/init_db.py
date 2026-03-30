#!/usr/bin/env python3
"""Initialize the database for the IoT Security Learning Tool."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db

app = create_app()

with app.app_context():
    db.create_all()
    print("Database initialized successfully.")
    print(f"Database location: {app.config['SQLALCHEMY_DATABASE_URI']}")
