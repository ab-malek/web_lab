# Pharmacy Inventory Management System

A complete Django web application for managing pharmacy inventory with role-based access control, sales tracking, and automated alerts.

 Quick Setup - Pharmacy Inventory System
 ======================================
python -m venv venv
.\venv\Scripts\Activate

 Installing dependencies...
pip install Django==4.2.7 reportlab==4.0.4

 Creating database structure...
python manage.py makemigrations
python manage.py migrate

 Setup complete! Now run:
 python manage.py createsuperuser
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

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Step 1: Install Dependencies
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### Step 2: Database Setup
The setup script will handle migrations and create initial data:

\`\`\`bash
python scripts/setup_database.py
\`\`\`

This script will:
1. Create migration files (`makemigrations`)
2. Apply migrations to create database tables (`migrate`)
3. Create a superuser account
4. Create sample user accounts for testing
5. Add sample medicine data

### Step 3: (Optional) Add More Sample Data
\`\`\`bash
python scripts/create_sample_data.py
\`\`\`

### Step 4: Start the Development Server
\`\`\`bash
python manage.py runserver
\`\`\`

The application will be available at: `http://127.0.0.1:8000/`

## Default Login Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Manager | manager1 | manager123 |
| Sales Staff | sales1 | sales123 |

## Manual Migration (Alternative Setup)

If you prefer to run migrations manually:

\`\`\`bash
# Create migration files
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Start server
python manage.py runserver
\`\`\`

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

## Customization

The system is built with Django best practices and can be easily extended:

- Add new user roles in `models.py`
- Extend product information in the Medicine model
- Add new report types in `views.py`
- Customize the UI by modifying templates

## Troubleshooting

### Common Issues

1. **Migration Errors**: Delete `db.sqlite3` and run setup script again
2. **Permission Denied**: Ensure proper user roles are assigned
3. **Template Not Found**: Check `TEMPLATES` setting in `settings.py`

### Getting Help

- Check Django documentation for framework-specific issues
- Review the code comments for implementation details
- Use Django admin interface for direct database access

## Production Deployment

Before deploying to production:

1. Change `SECRET_KEY` in settings.py
2. Set `DEBUG = False`
3. Configure proper database (PostgreSQL/MySQL)
4. Set up static file serving
5. Configure email settings for notifications
6. Set up proper logging

## License

This project is for educational and commercial use.
