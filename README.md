# Pharmacy Inventory Management System

A complete Django web application for managing pharmacy inventory with role-based access control, sales tracking, and automated alerts.

 Quick Setup - Pharmacy Inventory System
 ======================================
## For powershell

python -m venv venv

.\venv\Scripts\Activate.ps1

pip install Django==4.2.7 reportlab==4.0.4

Now run the server : 

 python manage.py runserver



## Features

- **User Authentication & Role-Based Access Control**
  - Admin: Full system access including user management
  - Manager: Product management, sales, and reports
  - Sales Staff: Sales transactions only

- **Product Management**
  - Add/view medicines with batch tracking
  - Automatic low stock alerts (< 10 units)
  - Expiry date monitoring (30-day alerts)

- **Sales & Invoicing**
  - Point-of-sale interface
  - Automatic invoice generation
  - PDF invoice downloads
  - Stock level updates

- **Dashboard & Reports**
  - Role-specific dashboards
  - Sales analytics
  - Stock status overview
  - Top-selling products





## Project Structure

\`\`\`
pharmacy_inventory/
├── pharmacy_inventory/          # Main project settings
├── inventory/                   # Main application
│   ├── models.py               # Database models
│   ├── views.py                # View functions
│   ├── forms.py                # Django forms
│   ├── admin.py                # Admin interface
│   ├── urls.py                 # URL routing
│   └── migrations/             # Database migrations
├── templates/                   # HTML templates
├── scripts/                     # Setup scripts
├── requirements.txt            # Python dependencies
└── manage.py                   # Django management script
\`\`\`

## Usage

### For Sales Staff
1. Login with sales credentials
2. Use "Sell Product" to process sales
3. Generate and download invoices
4. View personal sales dashboard

### For Managers
1. Access all sales staff features
2. Add new medicines to inventory
3. View stock alerts and reports
4. Monitor sales analytics

### For Admins
1. Access all system features
2. Manage user accounts
3. Full inventory control
4. System administration via Django admin

## Database Models

- **UserProfile**: Extends Django User with role information
- **Medicine**: Product information with batch tracking
- **Sale**: Individual sale transactions
- **Invoice**: Generated invoices linking multiple sales

## Security Features

- Role-based access control with decorators
- CSRF protection on all forms
- User authentication required for all views
- Permission checks on sensitive operations


## License

This project is for educational and commercial use.
