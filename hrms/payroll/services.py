"""
payroll/services.py
Business logic layer for Payroll management.
Handles salary calculation, period validation, and payment status transitions.
"""
from datetime import date
from django.db import transaction

from core.exceptions import PayrollAlreadyExistsError, InvalidPayrollStateError
from core.utils import calculate_gross_salary, calculate_net_salary
from core.models import CompanyConfig
from attendance.services import AttendanceService
from .models import Payroll


class PayrollService:
    """
    Encapsulates all business logic for payroll processing.
    Enforces uniqueness constraints and calculates salary breakdowns.
    """

    @staticmethod
    def _check_duplicate(employee_id: int, month: int, year: int,
                         exclude_pk: int = None):
        """
        Raise PayrollAlreadyExistsError if a payroll record already exists
        for this employee/month/year combination.
        """
        qs = Payroll.objects.filter(
            employee_id=employee_id, month=month, year=year
        )
        if exclude_pk:
            qs = qs.exclude(pk=exclude_pk)
        if qs.exists():
            from employees.models import Employee
            try:
                emp = Employee.objects.get(pk=employee_id)
                name = emp.get_full_name()
            except Employee.DoesNotExist:
                name = f"Employee #{employee_id}"
            raise PayrollAlreadyExistsError(name, month, year)

    @staticmethod
    @transaction.atomic
    def create_payroll(validated_data: dict) -> Payroll:
        """
        Create a new payroll record with auto-calculated gross and net.

        Raises:
            PayrollAlreadyExistsError: If payroll already exists for this period.

        Returns:
            Payroll: Newly created and calculated instance.
        """
        employee = validated_data.get('employee')
        month = validated_data.get('month')
        year = validated_data.get('year')

        PayrollService._check_duplicate(employee.pk, month, year)

        payroll = Payroll(**validated_data)
        payroll.gross_salary = calculate_gross_salary(payroll)
        payroll.net_salary = calculate_net_salary(payroll)
        payroll.full_clean()
        payroll.save()
        return payroll

    @staticmethod
    @transaction.atomic
    def update_payroll(pk: int, validated_data: dict) -> Payroll:
        """
        Update a payroll record and recalculate gross/net.

        Raises:
            InvalidPayrollStateError: If payroll is already marked as 'paid'.
        """
        from django.shortcuts import get_object_or_404
        payroll = get_object_or_404(Payroll, pk=pk)

        if payroll.status == 'paid':
            raise InvalidPayrollStateError(
                "Cannot edit a payroll record that has already been paid."
            )

        employee = validated_data.get('employee', payroll.employee)
        month = validated_data.get('month', payroll.month)
        year = validated_data.get('year', payroll.year)
        PayrollService._check_duplicate(employee.pk, month, year, exclude_pk=pk)

        for field, value in validated_data.items():
            setattr(payroll, field, value)

        payroll.gross_salary = calculate_gross_salary(payroll)
        payroll.net_salary = calculate_net_salary(payroll)
        payroll.save()
        return payroll

    @staticmethod
    @transaction.atomic
    def mark_as_paid(pk: int) -> Payroll:
        """
        Transition a payroll record to 'paid' status.

        Raises:
            InvalidPayrollStateError: If payroll is already paid or in draft.
        """
        from django.shortcuts import get_object_or_404
        payroll = get_object_or_404(Payroll, pk=pk)

        if payroll.status == 'paid':
            raise InvalidPayrollStateError("Payroll is already marked as paid.")

        payroll.status = 'paid'
        payroll.payment_date = date.today()
        payroll.save(update_fields=['status', 'payment_date', 'updated_at'])
        return payroll

    @staticmethod
    def get_monthly_summary(month: int, year: int) -> dict:
        """
        Return aggregated statistics for a given pay period.

        Returns:
            dict: total_records, total_gross, total_net, paid_count, draft_count
        """
        return Payroll.objects.get_period_summary(month, year)

    @staticmethod
    def get_period_list(month: int, year: int):
        """Return optimised queryset for a pay period list view."""
        return Payroll.objects.for_period(month, year)

    @staticmethod
    def prefill_from_employee(employee) -> dict:
        """
        Generate default payroll data from an employee's profile.
        Used to pre-populate the payroll creation form.

        Returns:
            dict: Initial form data.
        """
        today = date.today()
        target_month = today.month - 1 if today.month > 1 else 12
        target_year = today.year if today.month > 1 else today.year - 1

        try:
            config = CompanyConfig.load()
        except Exception:
            # Fallback defaults if singleton errors out
            config = type('Config', (), {'hra_percentage': 40.0, 'pf_percentage': 12.0})

        hra_pct = __import__('decimal').Decimal(str(config.hra_percentage / 100))
        pf_pct = __import__('decimal').Decimal(str(config.pf_percentage / 100))
        
        hra = employee.basic_salary * hra_pct
        pf = employee.basic_salary * pf_pct
        
        # Calculate Unpaid Attendance Days
        attendance_summary = AttendanceService.get_monthly_summary(employee.pk, target_month, target_year)
        unpaid_days = attendance_summary.get('total_unpaid_days', 0)
        
        # Calculate Per-Day deduction
        import calendar
        _, days_in_month = calendar.monthrange(target_year, target_month)
        per_day_salary = float(employee.basic_salary) / days_in_month
        leave_deductions = round(unpaid_days * per_day_salary, 2)

        notes = ""
        if unpaid_days > 0:
            notes = f"Auto-deducted ₹{leave_deductions} for {unpaid_days} unpaid days (Absent/Half-Day)."
            
        return {
            'employee': employee,
            'basic_salary': employee.basic_salary,
            'hra': round(hra, 2),
            'pf_deduction': round(pf, 2),
            'leave_deductions': leave_deductions,
            'month': target_month,
            'year': target_year,
            'notes': notes,
        }
