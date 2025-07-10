from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('sales_staff', 'Sales Staff'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='sales_staff')
    phone = models.CharField(max_length=15, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"


class Medicine(models.Model):
    name = models.CharField(max_length=200)
    generic_name = models.CharField(max_length=255)
    batch_number = models.CharField(max_length=100)
    quantity = models.IntegerField()
    expiry_date = models.DateField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    manufacturer = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['name', 'batch_number']
    
    def __str__(self):
        return f"{self.name} - {self.batch_number}"
    
    @property
    def is_low_stock(self):
        return self.quantity < 10
    
    @property
    def is_expiring_soon(self):
        return self.expiry_date <= (timezone.now().date() + timedelta(days=30))
    
    @property
    def is_expired(self):
        return self.expiry_date < timezone.now().date()


class Sale(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity_sold = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    sale_date = models.DateTimeField(auto_now_add=True)
    sold_by = models.ForeignKey(User, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=200, blank=True)
    
    def __str__(self):
        return f"Sale #{self.id} - {self.medicine.name}"
    
    def save(self, *args, **kwargs):
        self.total_amount = self.quantity_sold * self.unit_price
        super().save(*args, **kwargs)


class Invoice(models.Model):
    invoice_number = models.CharField(max_length=50, unique=True)
    sales = models.ManyToManyField(Sale)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=200, blank=True)
    
    def __str__(self):
        return f"Invoice #{self.invoice_number}"
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = f"INV{timezone.now().strftime('%Y%m%d')}{self.id or ''}"
        super().save(*args, **kwargs)
