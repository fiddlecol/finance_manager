#!/usr/bin/env python
"""
Initialize admin user for the application
Run: python create_admin.py
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User

def create_admin():
    """Create initial admin user"""
    app = create_app()
    
    with app.app_context():
        # Check if admin user exists
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print("✓ Admin user already exists")
            return
        
        # Create new admin user
        admin = User(
            username='admin',
            email='admin@finance.local'
        )
        admin.set_password('admin123')  # Change this to a secure password!
        
        db.session.add(admin)
        db.session.commit()
        
        print("✓ Admin user created successfully!")
        print("  Username: admin")
        print("  Password: admin123")
        print("\n⚠️  WARNING: Change the default password immediately in production!")

if __name__ == '__main__':
    create_admin()
