#!/usr/bin/env python
"""
Script to create additional sample data for testing
"""
import os
import sys
import django
from datetime import datetime, timedelta
import random

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_inventory.settings')
django.setup()

from django.contrib.auth.models import User
from inventory.models import Medicine, Sale, Invoice
from django.utils import timezone

def create_sample_sales():
    """Create sample sales data for testing reports"""
    medicines = Medicine.objects.all()
    users = User.objects.filter(userprofile__role__in=['sales_staff', 'manager'])
    
    if not medicines.exists() or not users.exists():
        print("Please run setup_database.py first to create medicines and users")
        return
    
    # Create sales for the last 30 days
    for i in range(50):  # Create 50 sample sales
        medicine = random.choice(medicines)
        user = random.choice(users)
        
        # Random date within last 30 days
        days_ago = random.randint(0, 30)
        sale_date = timezone.now() - timedelta(days=days_ago)
        
        # Random quantity (1-5)
        quantity = random.randint(1, min(5, medicine.quantity))
        
        if quantity > 0:
            sale = Sale.objects.create(
                medicine=medicine,
                quantity_sold=quantity,
                unit_price=medicine.price,
                sold_by=user,
                customer_name=random.choice([
                    'John Doe', 'Jane Smith', 'Bob Johnson', 
                    'Alice Brown', 'Charlie Wilson', ''
                ])
            )
            sale.sale_date = sale_date
            sale.save()
            
            # Update medicine quantity
            medicine.quantity -= quantity
            medicine.save()
            
            # Create invoice
            invoice = Invoice.objects.create(
                total_amount=sale.total_amount,
                created_by=user,
                customer_name=sale.customer_name
            )
            invoice.sales.add(sale)
            invoice.invoice_number = f"INV{sale_date.strftime('%Y%m%d')}{invoice.id:04d}"
            invoice.created_at = sale_date
            invoice.save()
            
            print(f"✓ Created sale: {medicine.name} x{quantity} = ${sale.total_amount}")

def main():
    print("Creating sample sales data...")
    print("=" * 40)
    
    create_sample_sales()
    
    print("\n" + "=" * 40)
    print("Sample data created successfully!")
    print("You can now view sales reports and dashboard statistics.")

if __name__ == '__main__':
    main()
