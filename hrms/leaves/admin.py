from django.contrib import admin
from .models import LeaveRequest, LeaveType


@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'max_days_per_year', 'is_paid']


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'start_date', 'end_date', 'status', 'applied_on']
    list_filter = ['status', 'leave_type']
    search_fields = ['employee__first_name', 'employee__last_name']
