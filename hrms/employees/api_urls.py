from django.urls import path
from .api_views import (
    EmployeeListCreateAPIView, 
    EmployeeRetrieveUpdateAPIView,
    DepartmentListAPIView
)

urlpatterns = [
    # Employee API
    path('', EmployeeListCreateAPIView.as_view(), name='api_employee_list_create'),
    path('<int:pk>/', EmployeeRetrieveUpdateAPIView.as_view(), name='api_employee_detail'),
    
    # Department API
    path('departments/', DepartmentListAPIView.as_view(), name='api_department_list'),
]
