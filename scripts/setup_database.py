#!/usr/bin/env python
"""
Setup script to create database tables and initial data
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_inventory.settings')
django.setup()

from django.contrib.auth.models import User
from inventory.models import UserProfile, Medicine
from datetime import datetime, timedelta

def create_superuser():
    """Create a superuser if it doesn't exist"""
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
            phone='123-456-7890'
        )
        print("✓ Admin user created (username: admin, password: admin123)")
    else:
        print("✓ Admin user already exists")

def create_sample_users():
    """Create sample users for different roles"""
    users_data = [
        {
            'username': 'manager1',
            'password': 'manager123',
            'first_name': 'John',
            'last_name': 'Manager',
            'email': 'manager@pharmacy.com',
            'role': 'manager',
            'phone': '123-456-7891'
        },
        {
            'username': 'sales1',
            'password': 'sales123',
            'first_name': 'Jane',
            'last_name': 'Sales',
            'email': 'sales@pharmacy.com',
            'role': 'sales_staff',
            'phone': '123-456-7892'
        }
    ]
    
    for user_data in users_data:
        if not User.objects.filter(username=user_data['username']).exists():
            user = User.objects.create_user(
                username=user_data['username'],
                password=user_data['password'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                email=user_data['email']
            )
            UserProfile.objects.create(
                user=user,
                role=user_data['role'],
                phone=user_data['phone']
            )
            print(f"✓ {user_data['role']} user created: {user_data['username']}")
        else:
            print(f"✓ User {user_data['username']} already exists")

def create_sample_medicines():
    """Create sample medicines for testing"""
    medicines_data = [
        {
            'name': 'Paracetamol 500mg',
            'batch_number': 'PAR001',
            'quantity': 100,
            'price': 5.99,
            'manufacturer': 'PharmaCorp',
            'expiry_date': datetime.now().date() + timedelta(days=365)
        },
        {
            'name': 'Ibuprofen 400mg',
            'batch_number': 'IBU001',
            'quantity': 8,  # Low stock
            'price': 7.50,
            'manufacturer': 'MediCorp',
            'expiry_date': datetime.now().date() + timedelta(days=180)
        },
        {
            'name': 'Amoxicillin 250mg',
            'batch_number': 'AMX001',
            'quantity': 50,
            'price': 12.99,
            'manufacturer': 'AntibioTech',
            'expiry_date': datetime.now().date() + timedelta(days=25)  # Expiring soon
        },
        {
            'name': 'Aspirin 100mg',
            'batch_number': 'ASP001',
            'quantity': 75,
            'price': 4.25,
            'manufacturer': 'CardioMed',
            'expiry_date': datetime.now().date() + timedelta(days=300)
        },
        {
            'name': 'Vitamin C 1000mg',
            'batch_number': 'VTC001',
            'quantity': 5,  # Low stock
            'price': 15.99,
            'manufacturer': 'VitaHealth',
            'expiry_date': datetime.now().date() + timedelta(days=15)  # Expiring soon
        }
    ]
    
    for med_data in medicines_data:
        if not Medicine.objects.filter(
            name=med_data['name'], 
            batch_number=med_data['batch_number']
        ).exists():
            Medicine.objects.create(**med_data)
            print(f"✓ Medicine created: {med_data['name']} - {med_data['batch_number']}")
        else:
            print(f"✓ Medicine already exists: {med_data['name']} - {med_data['batch_number']}")

def main():
    print("Setting up Pharmacy Inventory Management System...")
    print("=" * 50)
    
    # Make migrations first
    print("Creating migration files...")
    execute_from_command_line(['manage.py', 'makemigrations'])
    print("✓ Migration files created")
    
    # Run migrations
    print("Running database migrations...")
    execute_from_command_line(['manage.py', 'migrate'])
    print("✓ Database migrations completed")
    
    # Create users
    print("\nCreating users...")
    create_superuser()
    create_sample_users()
    
    # Create sample medicines
    print("\nCreating sample medicines...")
    create_sample_medicines()
    
    print("\n" + "=" * 50)
    print("Setup completed successfully!")
    print("\nLogin credentials:")
    print("Admin: username=admin, password=admin123")
    print("Manager: username=manager1, password=manager123")
    print("Sales Staff: username=sales1, password=sales123")
    print("\nRun 'python manage.py runserver' to start the application")

if __name__ == '__main__':
    main()
