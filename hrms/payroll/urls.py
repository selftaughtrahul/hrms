"""
payroll/urls.py — Updated to use Class-Based View .as_view()
"""
from django.urls import path
from .views import (
    PayrollListView, PayrollDetailView, PayrollCreateView,
    PayrollUpdateView, PayrollDeleteView,
    PayrollMarkPaidView, PayslipView,
)

urlpatterns = [
    path('', PayrollListView.as_view(), name='payroll_list'),
    path('<int:pk>/', PayrollDetailView.as_view(), name='payroll_detail'),
    path('create/', PayrollCreateView.as_view(), name='payroll_create'),
    path('<int:pk>/edit/', PayrollUpdateView.as_view(), name='payroll_edit'),
    path('<int:pk>/delete/', PayrollDeleteView.as_view(), name='payroll_delete'),
    path('<int:pk>/mark-paid/', PayrollMarkPaidView.as_view(), name='payroll_mark_paid'),
    path('<int:pk>/payslip/', PayslipView.as_view(), name='payslip'),
]
