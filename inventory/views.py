from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from datetime import timedelta
from .models import Medicine, Sale, Invoice, UserProfile
from .forms import CustomUserCreationForm, MedicineForm, SaleForm
from .decorators import role_required
from .utils import generate_invoice_pdf
import json


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # Role-based redirection
            try:
                profile = user.userprofile
                if profile.role == 'sales_staff':
                    return redirect('sell_product')
                else:
                    return redirect('dashboard')
            except UserProfile.DoesNotExist:
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'registration/login.html')


@login_required
def dashboard(request):
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        # Create a default profile if it doesn't exist
        user_profile = UserProfile.objects.create(
            user=request.user,
            role='sales_staff'
        )
    
    # Common data for all roles
    total_medicines = Medicine.objects.count()
    low_stock_medicines = Medicine.objects.filter(quantity__lt=10)
    expiring_medicines = Medicine.objects.filter(
        expiry_date__lte=timezone.now().date() + timedelta(days=30),
        expiry_date__gt=timezone.now().date()
    )
    
    # Top selling medicines in last 30 days
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    top_medicines = (
        Sale.objects.filter(sale_date__date__gte=thirty_days_ago)
        .values('medicine__name')
        .annotate(total_sold=Sum('quantity_sold'))
        .order_by('-total_sold')[:5]
    )

    context = {
        'user_profile': user_profile,
        'total_medicines': total_medicines,
        'low_stock_count': low_stock_medicines.count(),
        'expiring_count': expiring_medicines.count(),
        'low_stock_medicines': low_stock_medicines[:5],
        'expiring_medicines': expiring_medicines[:5],
        'top_medicines': top_medicines,
    }
    
    # Role-specific data
    if user_profile.role in ['admin', 'manager']:
        recent_sales = Sale.objects.select_related('medicine', 'sold_by').order_by('-sale_date')[:10]
        total_sales_today = Sale.objects.filter(
            sale_date__date=timezone.now().date()
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        context.update({
            'recent_sales': recent_sales,
            'total_sales_today': total_sales_today,
        })
    
    if user_profile.role == 'sales_staff':
        my_sales_today = Sale.objects.filter(
            sold_by=request.user,
            sale_date__date=timezone.now().date()
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        context.update({
            'my_sales_today': my_sales_today,
        })
    
    return render(request, 'inventory/dashboard.html', context)


@login_required
@role_required(['admin', 'manager'])
def add_product(request):
    if request.method == 'POST':
        form = MedicineForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Medicine added successfully!')
            return redirect('product_list')
    else:
        form = MedicineForm()
    
    return render(request, 'inventory/add_product.html', {'form': form})


@login_required
@role_required(['admin', 'manager'])
def product_list(request):
    # Sorting
    sort = request.GET.get('sort', 'name')
    direction = request.GET.get('dir', 'asc')
    from django.db.models.functions import Lower
    valid_fields = {
        'name': 'name',
        'generic_name': 'generic_name',
        'batch_number': 'batch_number',
        'quantity': 'quantity',
        'price': 'price',
        'expiry_date': 'expiry_date',
        'manufacturer': 'manufacturer',
        'created_at': 'created_at',
    }
    order_field = valid_fields.get(sort, 'name')
    string_fields = ['name', 'generic_name', 'batch_number', 'manufacturer']
    qs = Medicine.objects.all()
    if order_field.lstrip('-') in string_fields:
        # Use Lower() for case-insensitive sorting
        if direction == 'desc':
            qs = qs.annotate(_order=Lower(order_field.lstrip('-'))).order_by('-_order')
        else:
            qs = qs.annotate(_order=Lower(order_field)).order_by('_order')
    else:
        if direction == 'desc':
            qs = qs.order_by('-' + order_field.lstrip('-'))
        else:
            qs = qs.order_by(order_field)
    context = {
        'medicines': qs,
        'sort': sort,
        'dir': direction,
    }
    return render(request, 'inventory/product_list.html', context)


@login_required
def sell_product(request):
    if request.method == 'POST':
        # Handle completing the sale
        cart_data = request.POST.get('cart_data')
        customer_name = request.POST.get('customer_name', '')
        
        if not cart_data:
            messages.error(request, 'No items in cart to process.')
            return redirect('sell_product')
        
        try:
            cart_items = json.loads(cart_data)
            if not cart_items:
                messages.error(request, 'Cart is empty.')
                return redirect('sell_product')
            
            # Create invoice first
            invoice = Invoice.objects.create(
                total_amount=0,  # Will be updated after adding sales
                created_by=request.user,
                customer_name=customer_name
            )
            
            total_amount = 0
            sales_created = []
            
            # Process each item in cart
            for item in cart_items:
                medicine_id = item.get('medicine_id')
                quantity = int(item.get('quantity', 0))
                
                if quantity <= 0:
                    continue
                
                try:
                    medicine = Medicine.objects.get(id=medicine_id)
                    
                    # Check stock availability
                    if quantity > medicine.quantity:
                        messages.error(request, f'Only {medicine.quantity} units of {medicine.name} available.')
                        # Delete the invoice if we created it
                        invoice.delete()
                        return redirect('sell_product')
                    
                    # Create sale
                    sale = Sale.objects.create(
                        medicine=medicine,
                        quantity_sold=quantity,
                        unit_price=medicine.price,
                        sold_by=request.user,
                        customer_name=customer_name
                    )
                    
                    # Update medicine quantity
                    medicine.quantity -= quantity
                    medicine.save()
                    
                    # Add to invoice
                    invoice.sales.add(sale)
                    total_amount += sale.total_amount
                    sales_created.append(sale)
                    
                except Medicine.DoesNotExist:
                    messages.error(request, f'Medicine with ID {medicine_id} not found.')
                    # Rollback: delete invoice and any sales created
                    invoice.delete()
                    for sale in sales_created:
                        # Restore medicine quantity
                        sale.medicine.quantity += sale.quantity_sold
                        sale.medicine.save()
                        sale.delete()
                    return redirect('sell_product')
            
            # Update invoice total and generate invoice number
            invoice.total_amount = total_amount
            invoice.invoice_number = f"INV{timezone.now().strftime('%Y%m%d')}{invoice.id:04d}"
            invoice.save()
            
            messages.success(request, f'Sale completed! Invoice #{invoice.invoice_number} generated with {len(sales_created)} items.')
            return redirect('invoice_detail', invoice_id=invoice.id)
            
        except (json.JSONDecodeError, ValueError) as e:
            messages.error(request, 'Invalid cart data.')
            return redirect('sell_product')
    
    # GET request - show the sell form
    available_medicines = Medicine.objects.filter(
        quantity__gt=0,
        expiry_date__gt=timezone.now().date()
    ).order_by('name')
    
    return render(request, 'inventory/sell_product.html', {
        'available_medicines': available_medicines
    })


@login_required
def get_medicine_info(request, medicine_id):
    """AJAX endpoint to get medicine information"""
    try:
        medicine = Medicine.objects.get(id=medicine_id)
        data = {
            'id': medicine.id,
            'name': medicine.name,
            'batch_number': medicine.batch_number,
            'price': float(medicine.price),
            'quantity': medicine.quantity,
            'manufacturer': medicine.manufacturer,
            'expiry_date': medicine.expiry_date.strftime('%Y-%m-%d')
        }
        return JsonResponse(data)
    except Medicine.DoesNotExist:
        return JsonResponse({'error': 'Medicine not found'}, status=404)


@login_required
def invoice_detail(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    return render(request, 'inventory/invoice_detail.html', {'invoice': invoice})


@login_required
def download_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.invoice_number}.pdf"'
    
    pdf_content = generate_invoice_pdf(invoice)
    response.write(pdf_content)
    
    return response


@login_required
@role_required(['admin'])
def manage_users(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User "{user.username}" created successfully!')
            # Redirect to the same page to clear the form
            return redirect('manage_users')
        else:
            # If form is invalid, it will be passed to template with errors
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    
    users = UserProfile.objects.select_related('user').all().order_by('-user__date_joined')
    return render(request, 'inventory/manage_users.html', {'form': form, 'users': users})


@login_required
@role_required(['admin', 'manager'])
def alerts(request):
    # Get current date for calculations
    today = timezone.now().date()
    thirty_days_from_now = today + timedelta(days=30)
    
    # Low stock medicines (quantity < 10)
    low_stock_medicines = Medicine.objects.filter(quantity__lt=10).order_by('quantity', 'name')
    
    # Medicines expiring within 30 days (but not expired yet)
    expiring_medicines = Medicine.objects.filter(
        expiry_date__lte=thirty_days_from_now,
        expiry_date__gt=today
    ).order_by('expiry_date', 'name')
    
    # Already expired medicines
    expired_medicines = Medicine.objects.filter(
        expiry_date__lt=today
    ).order_by('expiry_date', 'name')
    
    # Debug: Print counts to console
    print(f"Low stock count: {low_stock_medicines.count()}")
    print(f"Expiring soon count: {expiring_medicines.count()}")
    print(f"Expired count: {expired_medicines.count()}")
    
    # Debug: Print some sample data
    if low_stock_medicines.exists():
        print("Sample low stock medicines:")
        for med in low_stock_medicines[:3]:
            print(f"  - {med.name}: {med.quantity} units")
    
    if expiring_medicines.exists():
        print("Sample expiring medicines:")
        for med in expiring_medicines[:3]:
            print(f"  - {med.name}: expires {med.expiry_date}")
    
    context = {
        'low_stock_medicines': low_stock_medicines,
        'expiring_medicines': expiring_medicines,
        'expired_medicines': expired_medicines,
        'today': today,
        'thirty_days_from_now': thirty_days_from_now,
    }
    
    return render(request, 'inventory/alerts.html', context)


@login_required
@role_required(['admin', 'manager'])
def remove_medicine(request, medicine_id):
    """Remove a medicine from inventory"""
    if request.method == 'POST':
        try:
            medicine = get_object_or_404(Medicine, id=medicine_id)
            
            # Check if medicine has been sold (has sales records)
            sales_count = Sale.objects.filter(medicine=medicine).count()
            
            if sales_count > 0:
                # If medicine has sales history, we should keep the record but mark it as removed
                # For now, we'll just show a warning and not delete
                messages.warning(
                    request, 
                    f'Cannot delete "{medicine.name} - {medicine.batch_number}" because it has sales history. '
                    f'Consider setting quantity to 0 instead.'
                )
            else:
                # Safe to delete - no sales history
                medicine_name = f"{medicine.name} - {medicine.batch_number}"
                medicine.delete()
                messages.success(request, f'Medicine "{medicine_name}" has been removed from inventory.')
            
        except Medicine.DoesNotExist:
            messages.error(request, 'Medicine not found.')
        except Exception as e:
            messages.error(request, f'Error removing medicine: {str(e)}')
    
    return redirect('alerts')


@login_required
@role_required(['admin', 'manager'])
def bulk_remove_expired(request):
    """Remove all expired medicines that have no sales history"""
    if request.method == 'POST':
        today = timezone.now().date()
        expired_medicines = Medicine.objects.filter(expiry_date__lt=today)
        
        removed_count = 0
        skipped_count = 0
        removed_medicines = []
        
        for medicine in expired_medicines:
            sales_count = Sale.objects.filter(medicine=medicine).count()
            
            if sales_count == 0:
                # Safe to delete
                removed_medicines.append(f"{medicine.name} - {medicine.batch_number}")
                medicine.delete()
                removed_count += 1
            else:
                # Skip - has sales history
                skipped_count += 1
        
        if removed_count > 0:
            messages.success(
                request, 
                f'Successfully removed {removed_count} expired medicines from inventory.'
            )
            
            # Log the removed medicines for reference
            if removed_medicines:
                print("Removed expired medicines:")
                for med_name in removed_medicines:
                    print(f"  - {med_name}")
        
        if skipped_count > 0:
            messages.info(
                request,
                f'{skipped_count} expired medicines were kept because they have sales history.'
            )
        
        if removed_count == 0 and skipped_count == 0:
            messages.info(request, 'No expired medicines found to remove.')
    
    return redirect('alerts')


@login_required
@role_required(['admin', 'manager'])
def sales_report(request):
    # Get sales data for the last 30 days
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    sales = Sale.objects.filter(sale_date__date__gte=thirty_days_ago).select_related('medicine', 'sold_by')
    
    # Calculate totals
    total_sales = sales.aggregate(total=Sum('total_amount'))['total'] or 0
    total_quantity = sales.aggregate(total=Sum('quantity_sold'))['total'] or 0
    
    # Top selling medicines
    top_medicines = sales.values('medicine__name').annotate(
        total_sold=Sum('quantity_sold'),
        total_revenue=Sum('total_amount')
    ).order_by('-total_sold')[:10]
    
    context = {
        'sales': sales.order_by('-sale_date'),
        'total_sales': total_sales,
        'total_quantity': total_quantity,
        'top_medicines': top_medicines,
    }
    
    return render(request, 'inventory/sales_report.html', context)
