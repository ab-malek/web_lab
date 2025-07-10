@echo off
echo Quick Setup - Pharmacy Inventory System
echo ======================================
python -m venv venv
.\venv\Scripts\Activate

echo Installing dependencies...
pip install Django==4.2.7 reportlab==4.0.4

echo Creating database structure...
python manage.py makemigrations
python manage.py migrate

echo Setup complete! Now run:
echo python manage.py createsuperuser
echo python manage.py runserver
pause

