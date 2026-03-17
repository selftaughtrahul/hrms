from rest_framework import serializers
from .models import LeaveRequest, LeaveType
from employees.serializers import EmployeeListSerializer

class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = ['id', 'name', 'description', 'max_days_per_year', 'is_paid']

class LeaveRequestSerializer(serializers.ModelSerializer):
    leave_type_details = LeaveTypeSerializer(source='leave_type', read_only=True)
    employee_details = EmployeeListSerializer(source='employee', read_only=True)
    
    class Meta:
        model = LeaveRequest
        fields = [
            'id', 'employee', 'employee_details', 'leave_type', 'leave_type_details',
            'start_date', 'end_date', 'total_days', 'reason',
            'status', 'applied_on', 'reviewed_by', 'review_note', 'reviewed_on',
            'attachment'
        ]
        read_only_fields = [
            'id', 'total_days', 'status', 'applied_on', 
            'reviewed_by', 'review_note', 'reviewed_on'
        ]
