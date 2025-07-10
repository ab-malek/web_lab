from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Medicine, Sale, UserProfile
from django.utils import timezone


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES, 
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    phone = forms.CharField(
        max_length=15, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes to password fields
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        
        # Add helpful labels
        self.fields['password1'].help_text = None  # Remove default help text
        self.fields['password2'].help_text = None  # Remove default help text
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Get or create the UserProfile (in case signals created it)
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'role': self.cleaned_data['role'],
                    'phone': self.cleaned_data['phone']
                }
            )
            # If profile already exists (created by signal), update it
            if not created:
                profile.role = self.cleaned_data['role']
                profile.phone = self.cleaned_data['phone']
                profile.save()
        return user


class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = [
            'name',
            'generic_name',   # <--- Add this line
            'batch_number',
            'quantity',
            'expiry_date',
            'price',
            'manufacturer',
        ]
        widgets = {
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'generic_name': forms.TextInput(attrs={'class': 'form-control'}),  # <--- Add this line
            'batch_number': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'manufacturer': forms.TextInput(attrs={'class': 'form-control'}),
        }



class SaleForm(forms.ModelForm):
    customer_name = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = Sale
        fields = ['medicine', 'quantity_sold', 'customer_name']
        widgets = {
            'medicine': forms.Select(attrs={'class': 'form-control'}),
            'quantity_sold': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show medicines that are in stock and not expired
        self.fields['medicine'].queryset = Medicine.objects.filter(
            quantity__gt=0,
            expiry_date__gt=timezone.now().date()
        )
    
    def clean(self):
        cleaned_data = super().clean()
        medicine = cleaned_data.get('medicine')
        quantity_sold = cleaned_data.get('quantity_sold')
        
        if medicine and quantity_sold:
            if quantity_sold > medicine.quantity:
                raise forms.ValidationError(f"Only {medicine.quantity} units available in stock.")
        
        return cleaned_data
