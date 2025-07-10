from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.user_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Product management
    path('add-product/', views.add_product, name='add_product'),
    path('products/', views.product_list, name='product_list'),
    
    # Sales
    path('sell/', views.sell_product, name='sell_product'),
    path('api/medicine/<int:medicine_id>/', views.get_medicine_info, name='get_medicine_info'),
    path('invoice/<int:invoice_id>/', views.invoice_detail, name='invoice_detail'),
    path('invoice/<int:invoice_id>/download/', views.download_invoice, name='download_invoice'),
    
    # Admin functions
    path('manage-users/', views.manage_users, name='manage_users'),
    path('alerts/', views.alerts, name='alerts'),
    path('remove-medicine/<int:medicine_id>/', views.remove_medicine, name='remove_medicine'),
    path('bulk-remove-expired/', views.bulk_remove_expired, name='bulk_remove_expired'),
    path('sales-report/', views.sales_report, name='sales_report'),
]
