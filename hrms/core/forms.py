from django import forms
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
