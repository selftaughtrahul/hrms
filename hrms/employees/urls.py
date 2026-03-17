"""
employees/urls.py — Updated to use Class-Based View .as_view()
"""
from django.urls import path
from .views import (
    EmployeeListView, EmployeeDetailView, EmployeeCreateView,
    EmployeeUpdateView, EmployeeDeleteView,
    DepartmentListView, DepartmentCreateView,
    DepartmentUpdateView, DepartmentDeleteView,
)

urlpatterns = [
    # Employee CRUD
    path('', EmployeeListView.as_view(), name='employee_list'),
    path('<int:pk>/', EmployeeDetailView.as_view(), name='employee_detail'),
    path('create/', EmployeeCreateView.as_view(), name='employee_create'),
    path('<int:pk>/edit/', EmployeeUpdateView.as_view(), name='employee_edit'),
    path('<int:pk>/delete/', EmployeeDeleteView.as_view(), name='employee_delete'),
    # Department CRUD
    path('departments/', DepartmentListView.as_view(), name='department_list'),
    path('departments/create/', DepartmentCreateView.as_view(), name='department_create'),
    path('departments/<int:pk>/edit/', DepartmentUpdateView.as_view(), name='department_edit'),
    path('departments/<int:pk>/delete/', DepartmentDeleteView.as_view(), name='department_delete'),
]
