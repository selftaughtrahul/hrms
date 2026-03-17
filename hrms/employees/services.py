"""
employees/services.py
Business logic layer for the Employee module.
Views call Service methods — never interact with models directly in views.
"""
from django.db import transaction
from django.shortcuts import get_object_or_404

from core.exceptions import DuplicateEmployeeIDError, EmployeeNotFoundError
from .models import Employee, Department


class EmployeeService:
    """
    Encapsulates all business operations for Employee management.
    All methods are static — services are stateless by design.
    """

    @staticmethod
    def get_employee(pk: int) -> Employee:
        """
        Retrieve a single employee by PK with related objects pre-loaded.

        Raises:
            EmployeeNotFoundError: If no employee exists with this PK.
        """
        try:
            return Employee.objects.with_relations().get(pk=pk)
        except Employee.DoesNotExist:
            raise EmployeeNotFoundError(f"Employee with ID {pk} does not exist.")

    @staticmethod
    @transaction.atomic
    def create_employee(validated_data: dict) -> Employee:
        """
        Create a new employee record.

        Args:
            validated_data: Cleaned data dict from EmployeeForm

        Raises:
            DuplicateEmployeeIDError: If employee_id is already taken.

        Returns:
            Employee: The newly created instance.
        """
        emp_id = validated_data.get('employee_id', '').strip()
        if Employee.objects.filter(employee_id=emp_id).exists():
            raise DuplicateEmployeeIDError(
                f"Employee ID '{emp_id}' is already in use."
            )
        employee = Employee(**validated_data)
        employee.full_clean()
        employee.save()
        return employee

    @staticmethod
    @transaction.atomic
    def update_employee(pk: int, validated_data: dict) -> Employee:
        """
        Update an existing employee record.

        Args:
            pk: Employee primary key
            validated_data: Cleaned data dict from EmployeeForm

        Returns:
            Employee: The updated instance.
        """
        employee = EmployeeService.get_employee(pk)
        for field, value in validated_data.items():
            setattr(employee, field, value)
        employee.full_clean()
        employee.save()
        return employee

    @staticmethod
    @transaction.atomic
    def deactivate_employee(pk: int) -> Employee:
        """
        Mark an employee as inactive (soft status change, not deletion).

        Returns:
            Employee: The deactivated instance.
        """
        employee = EmployeeService.get_employee(pk)
        employee.status = 'inactive'
        employee.save(update_fields=['status', 'updated_at'])
        return employee

    @staticmethod
    def get_dashboard_stats() -> dict:
        """
        Return aggregated employee statistics for the dashboard.

        Returns:
            dict: Counts of employees by type and total active.
        """
        return Employee.objects.get_stats()

    @staticmethod
    def get_filtered_list(query: str = '', emp_type: str = '',
                          department_id: str = '', status: str = ''):
        """
        Return a filtered, optimised employee queryset for the list view.

        Args:
            query: Search string (name / email / ID / designation)
            emp_type: Employee type filter string
            department_id: Department PK as string
            status: Status filter string

        Returns:
            QuerySet: Filtered Employee queryset with select_related applied.
        """
        qs = Employee.objects.with_relations()
        if query:
            qs = qs.search(query)
        if emp_type:
            qs = qs.by_type(emp_type)
        if department_id:
            try:
                qs = qs.by_department(int(department_id))
            except (ValueError, TypeError):
                pass
        if status:
            qs = qs.filter(status=status)
        return qs


class DepartmentService:
    """
    Encapsulates business operations for Department management.
    """

    @staticmethod
    def get_all():
        return Department.objects.all().order_by('name')

    @staticmethod
    @transaction.atomic
    def create_department(validated_data: dict) -> Department:
        dept = Department(**validated_data)
        dept.full_clean()
        dept.save()
        return dept

    @staticmethod
    @transaction.atomic
    def update_department(pk: int, validated_data: dict) -> Department:
        dept = get_object_or_404(Department, pk=pk)
        for field, value in validated_data.items():
            setattr(dept, field, value)
        dept.full_clean()
        dept.save()
        return dept
