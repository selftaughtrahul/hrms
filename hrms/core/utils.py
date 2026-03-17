"""
core/utils.py
Shared utility functions and helpers used across all HRMS modules.
"""
from decimal import Decimal
from datetime import date, timedelta


# ─── Salary Utilities ────────────────────────────────────────────────────────

def calculate_gross_salary(payroll) -> Decimal:
    """
    Calculate gross salary by summing all earnings components.
    
    Args:
        payroll: Payroll model instance
    Returns:
        Decimal: Gross salary amount
    """
    return (
        payroll.basic_salary
        + payroll.hra
        + payroll.travel_allowance
        + payroll.other_allowances
        + payroll.overtime_pay
    )


def calculate_total_deductions(payroll) -> Decimal:
    """
    Calculate total deductions from a payroll instance.
    
    Args:
        payroll: Payroll model instance
    Returns:
        Decimal: Total deductions amount
    """
    return (
        payroll.pf_deduction
        + payroll.tax_deduction
        + payroll.other_deductions
        + payroll.leave_deductions
    )


def calculate_net_salary(payroll) -> Decimal:
    """
    Calculate net salary (gross - deductions).
    
    Args:
        payroll: Payroll model instance
    Returns:
        Decimal: Net salary amount
    """
    gross = calculate_gross_salary(payroll)
    deductions = calculate_total_deductions(payroll)
    return max(Decimal('0.00'), gross - deductions)


# ─── Date Utilities ──────────────────────────────────────────────────────────

def get_working_days(start_date: date, end_date: date) -> int:
    """
    Count working days (Mon–Fri) between two dates inclusive.
    
    Args:
        start_date: Start date
        end_date: End date
    Returns:
        int: Number of working days
    """
    if start_date > end_date:
        return 0
    total = 0
    current = start_date
    while current <= end_date:
        if current.weekday() < 5:  # Mon=0 ... Fri=4
            total += 1
        current += timedelta(days=1)
    return total


def get_calendar_days(start_date: date, end_date: date) -> int:
    """
    Count total calendar days between two dates (inclusive).
    
    Args:
        start_date: Start date
        end_date: End date
    Returns:
        int: Number of calendar days
    """
    if start_date > end_date:
        return 0
    return (end_date - start_date).days + 1


def get_month_label(month_number: int) -> str:
    """Return full month name for a given month number (1–12)."""
    months = [
        '', 'January', 'February', 'March', 'April',
        'May', 'June', 'July', 'August', 'September',
        'October', 'November', 'December',
    ]
    if 1 <= month_number <= 12:
        return months[month_number]
    raise ValueError(f"Invalid month number: {month_number}")


# ─── Employee Utilities ──────────────────────────────────────────────────────

def generate_employee_id(prefix: str = 'EMP') -> str:
    """
    Auto-generate a unique employee ID.
    Format: EMP + zero-padded 3-digit number (e.g. EMP042)
    
    Args:
        prefix: ID prefix string
    Returns:
        str: Unique employee ID
    """
    from employees.models import Employee
    last = Employee.all_objects.order_by('-created_at').first()
    if last and last.employee_id.startswith(prefix):
        try:
            last_num = int(last.employee_id[len(prefix):])
            return f"{prefix}{last_num + 1:03d}"
        except ValueError:
            pass
    return f"{prefix}001"


def format_currency(amount) -> str:
    """Format a decimal amount as Indian currency string."""
    try:
        return f"₹{float(amount):,.2f}"
    except (TypeError, ValueError):
        return "₹0.00"
