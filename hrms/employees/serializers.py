from rest_framework import serializers
from .models import Employee, Department

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'description']

class EmployeeListSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    
    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'first_name', 'last_name', 
            'email', 'employee_type', 'status', 'department_name'
        ]

class EmployeeDetailSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), 
        source='department', 
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'first_name', 'last_name', 'email', 'phone', 
            'gender', 'date_of_birth', 'address', 'employee_type', 
            'department', 'department_id', 'designation', 'date_of_joining', 
            'status', 'basic_salary', 'hourly_rate', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
