from django import forms
from .models import Employee, Department


class EmployeeForm(forms.ModelForm):
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False
    )
    date_of_joining = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    date_of_leaving = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = Employee
        fields = [
            'employee_id', 'first_name', 'last_name', 'email', 'phone',
            'gender', 'date_of_birth', 'address',
            'employee_type', 'department', 'designation',
            'date_of_joining', 'date_of_leaving', 'status',
            'basic_salary', 'hourly_rate',
            'annual_leave_quota', 'sick_leave_quota',
        ]
        widgets = {
            'employee_id': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control form-select'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'employee_type': forms.Select(attrs={'class': 'form-control form-select'}),
            'department': forms.Select(attrs={'class': 'form-control form-select'}),
            'designation': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control form-select'}),
            'basic_salary': forms.NumberInput(attrs={'class': 'form-control'}),
            'hourly_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'annual_leave_quota': forms.NumberInput(attrs={'class': 'form-control'}),
            'sick_leave_quota': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
