#!/usr/bin/env python
"""
Manual setup script that can be run from project root
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

def main():
    """Run setup commands"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_inventory.settings')
    
    print("Setting up Pharmacy Inventory Management System...")
    print("=" * 50)
    
    try:
        # Make migrations
        print("Creating migration files...")
        execute_from_command_line(['manage.py', 'makemigrations'])
        print("✓ Migration files created")
        
        # Run migrations
        print("Running database migrations...")
        execute_from_command_line(['manage.py', 'migrate'])
        print("✓ Database migrations completed")
        
        print("\n" + "=" * 50)
        print("Basic setup completed!")
        print("\nNext steps:")
        print("1. Create a superuser: python manage.py createsuperuser")
        print("2. Start the server: python manage.py runserver")
        print("3. Visit: http://127.0.0.1:8000/admin to add users and data")
        
    except Exception as e:
        print(f"Error during setup: {e}")
        print("\nTry running commands manually:")
        print("python manage.py makemigrations")
        print("python manage.py migrate")
        print("python manage.py createsuperuser")

if __name__ == '__main__':
    main()
