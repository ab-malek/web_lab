from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, Medicine, Sale, Invoice


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'


class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ['name', 'batch_number', 'quantity', 'expiry_date', 'price', 'manufacturer', 'is_low_stock', 'is_expiring_soon']
    list_filter = ['manufacturer', 'expiry_date', 'created_at']
    search_fields = ['name', 'batch_number', 'manufacturer']
    list_editable = ['quantity', 'price']
    
    def is_low_stock(self, obj):
        return obj.is_low_stock
    is_low_stock.boolean = True
    is_low_stock.short_description = 'Low Stock'
    
    def is_expiring_soon(self, obj):
        return obj.is_expiring_soon
    is_expiring_soon.boolean = True
    is_expiring_soon.short_description = 'Expiring Soon'


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['id', 'medicine', 'quantity_sold', 'unit_price', 'total_amount', 'sale_date', 'sold_by']
    list_filter = ['sale_date', 'sold_by']
    search_fields = ['medicine__name', 'customer_name']
    readonly_fields = ['total_amount']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'total_amount', 'created_at', 'created_by', 'customer_name']
    list_filter = ['created_at', 'created_by']
    search_fields = ['invoice_number', 'customer_name']
    readonly_fields = ['invoice_number', 'total_amount']
