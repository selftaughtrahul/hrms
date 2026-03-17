from django import forms
from .models import Holiday


class HolidayForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    class Meta:
        model = Holiday
        fields = ['name', 'date', 'holiday_type', 'description', 'is_restricted']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'holiday_type': forms.Select(attrs={'class': 'form-control form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
