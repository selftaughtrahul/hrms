from django.contrib import admin
from .models import Employee, Department


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'first_name', 'last_name', 'employee_type', 'department', 'status', 'date_of_joining']
    list_filter = ['employee_type', 'status', 'department', 'gender']
    search_fields = ['employee_id', 'first_name', 'last_name', 'email']
    ordering = ['employee_id']
