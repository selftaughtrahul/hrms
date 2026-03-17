from django import forms
from .models import Payroll
from employees.models import Employee


class PayrollForm(forms.ModelForm):
    class Meta:
        model = Payroll
        fields = [
            'employee', 'month', 'year',
            'basic_salary', 'hra', 'travel_allowance', 'other_allowances', 'overtime_pay', 'hours_worked',
            'pf_deduction', 'tax_deduction', 'other_deductions', 'leave_deductions',
            'payment_date', 'payment_mode', 'notes', 'status',
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control form-select'}),
            'month': forms.Select(attrs={'class': 'form-control form-select'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'basic_salary': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'hra': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'travel_allowance': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'other_allowances': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'overtime_pay': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'hours_worked': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'pf_deduction': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'tax_deduction': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'other_deductions': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'leave_deductions': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'payment_mode': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-control form-select'}),
        }
