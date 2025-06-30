#!/usr/bin/env python
"""
Clean setup script - creates database tables and admin user only
No sample data included
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_inventory.settings')
django.setup()

from django.contrib.auth.models import User
from inventory.models import UserProfile

def create_admin_user():
    """Create admin user only"""
    if not User.objects.filter(username='admin').exists():
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@pharmacy.com',
            password='admin123',
            first_name='Admin',
            last_name='User'
        )
        UserProfile.objects.create(
            user=admin_user,
            role='admin',
            phone=''
        )
        print("✓ Admin user created (username: admin, password: admin123)")
    else:
        print("✓ Admin user already exists")

def main():
    print("Setting up Pharmacy Inventory Management System (Clean Install)...")
    print("=" * 60)
    
    # Make migrations first
    print("Creating migration files...")
    execute_from_command_line(['manage.py', 'makemigrations'])
    print("✓ Migration files created")
    
    # Run migrations
    print("Running database migrations...")
    execute_from_command_line(['manage.py', 'migrate'])
    print("✓ Database migrations completed")
    
    # Create admin user only
    print("\nCreating admin user...")
    create_admin_user()
    
    print("\n" + "=" * 60)
    print("Clean setup completed successfully!")
    print("\nLogin credentials:")
    print("Admin: username=admin, password=admin123")
    print("\nNext steps:")
    print("1. Run: python manage.py runserver")
    print("2. Visit: http://127.0.0.1:8000/")
    print("3. Login and start adding your own data")
    print("\nYou can also access Django Admin at: http://127.0.0.1:8000/admin/")

if __name__ == '__main__':
    main()
