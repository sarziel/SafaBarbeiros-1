import os
import sys
from app import create_app, db
from app.models import User, ROLE_ADMIN
from config import get_config

def create_admin_user(username, email, password):
    """Create an admin user in the database"""
    app = create_app(get_config())
    
    with app.app_context():
        # Check if admin user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            print(f"User with email {email} already exists.")
            return False
        
        # Create new admin user
        admin = User(
            nome=username,
            email=email,
            telefone="",  # Admin may not need a phone number
            role=ROLE_ADMIN
        )
        admin.set_password(password)
        
        # Add to database
        db.session.add(admin)
        db.session.commit()
        
        print(f"Admin user '{username}' created successfully!")
        return True

if __name__ == "__main__":
    # Create admin with username 'admin', email 'admin@example.com', password 'admin123'
    create_admin_user("admin", "admin@example.com", "admin123")