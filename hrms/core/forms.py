from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import CompanyConfig


class CompanyConfigForm(forms.ModelForm):
    class Meta:
        model = CompanyConfig
        fields = [
            'company_name', 'company_address', 'company_logo',
            'global_font_family', 'global_background_color', 'primary_color',
            'hra_percentage', 'pf_percentage'
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'company_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'company_logo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'global_font_family': forms.Select(
                choices=[
                    ("'Inter', sans-serif", "Inter"),
                    ("'Roboto', sans-serif", "Roboto"),
                    ("'Open Sans', sans-serif", "Open Sans"),
                    ("'Lato', sans-serif", "Lato"),
                    ("'Montserrat', sans-serif", "Montserrat"),
                    ("system-ui, -apple-system, sans-serif", "System Default"),
                ],
                attrs={'class': 'form-select'}
            ),
            'global_background_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'primary_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'hra_percentage': forms.NumberInput(attrs={'class': 'form-control'}),
            'pf_percentage': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class TenantSignupForm(forms.Form):
    """
    Public sign-up form used by companies to register for the HRMS SaaS.
    Creates a Tenant, a Django User, and a UserProfile in one step.
    """
    company_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Acme Corp',
            'id': 'id_company_name',
            'autofocus': True,
        }),
        label='Company Name',
    )
    admin_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'John Smith',
            'id': 'id_admin_name',
        }),
        label='Your Full Name',
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'admin@yourcompany.com',
            'id': 'id_email',
        }),
        label='Work Email',
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '••••••••',
            'id': 'id_password',
        }),
        min_length=8,
        label='Password',
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '••••••••',
            'id': 'id_confirm_password',
        }),
        label='Confirm Password',
    )

    def clean_email(self):
        email = self.cleaned_data['email'].lower().strip()
        if User.objects.filter(email=email).exists():
            raise ValidationError('An account with this email already exists.')
        from core.models import Tenant
        if Tenant.objects.filter(owner_email=email).exists():
            raise ValidationError('A company is already registered with this email.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match.')
        return cleaned_data
