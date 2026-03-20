from django import forms
from .models import LeaveRequest, LeaveType
from employees.models import Employee


class LeaveRequestForm(forms.ModelForm):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    class Meta:
        model = LeaveRequest
        fields = ['employee', 'leave_type', 'start_date', 'end_date', 'reason']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control form-select'}),
            'leave_type': forms.Select(attrs={'class': 'form-control form-select'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter dropdowns by tenant
        self.fields['employee'].queryset = Employee.objects.all()
        self.fields['leave_type'].queryset = LeaveType.objects.all()


class LeaveReviewForm(forms.Form):
    STATUS_CHOICES = [
        ('approved', 'Approve'),
        ('rejected', 'Reject'),
    ]
    status = forms.ChoiceField(choices=STATUS_CHOICES, widget=forms.Select(attrs={'class': 'form-control form-select'}))
    review_note = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False
    )


class LeaveTypeForm(forms.ModelForm):
    class Meta:
        model = LeaveType
        fields = ['name', 'description', 'max_days_per_year', 'is_paid']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'max_days_per_year': forms.NumberInput(attrs={'class': 'form-control'}),
        }
