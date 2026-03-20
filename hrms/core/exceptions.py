"""
core/exceptions.py
Domain-specific exceptions for the HRMS system.
Provides clear, meaningful error types for business logic failures.
"""


class HRMSBaseException(Exception):
    """Base exception for all HRMS domain errors."""
    default_message = "An HRMS error occurred."

    def __init__(self, message=None):
        self.message = message or self.default_message
        super().__init__(self.message)

    def __str__(self):
        return self.message


# ─── Employee Exceptions ────────────────────────────────────────────────────

class EmployeeNotFoundError(HRMSBaseException):
    """Raised when an employee record cannot be found."""
    default_message = "Employee not found."


class DuplicateEmployeeIDError(HRMSBaseException):
    """Raised when attempting to create an employee with an existing ID."""
    default_message = "An employee with this ID already exists."


# ─── Leave Exceptions ────────────────────────────────────────────────────────

class LeaveNotFoundError(HRMSBaseException):
    """Raised when a leave request cannot be found."""
    default_message = "Leave request not found."


class LeaveConflictError(HRMSBaseException):
    """Raised when overlapping leave requests are detected."""
    default_message = "An overlapping leave request already exists for this period."


class InvalidLeaveStatusTransitionError(HRMSBaseException):
    """Raised when an invalid leave status transition is attempted."""
    default_message = "This leave request cannot be updated in its current state."

    def __init__(self, current_status, target_status):
        self.current_status = current_status
        self.target_status = target_status
        message = (
            f"Cannot transition leave from '{current_status}' to '{target_status}'."
        )
        super().__init__(message)


class InsufficientLeaveBalanceError(HRMSBaseException):
    """Raised when an employee has insufficient leave balance."""
    default_message = "Insufficient leave balance for this request."


# ─── Payroll Exceptions ──────────────────────────────────────────────────────

class PayrollAlreadyExistsError(HRMSBaseException):
    """Raised when payroll for a given employee/month/year already exists."""
    default_message = "Payroll entry already exists for this employee and period."

    def __init__(self, employee_name, month, year):
        message = (
            f"Payroll for {employee_name} for {month}/{year} already exists."
        )
        super().__init__(message)


class PayrollNotFoundError(HRMSBaseException):
    """Raised when a payroll record cannot be found."""
    default_message = "Payroll record not found."


class InvalidPayrollStateError(HRMSBaseException):
    """Raised when a payroll operation is invalid given the current status."""
    default_message = "This payroll operation is not valid in the current state."
