"""
leaves/services.py
Business logic layer for Leave management.
Enforces status transition rules and leave validation.
"""
from django.db import transaction
from django.utils import timezone

from core.exceptions import (
    LeaveNotFoundError,
    LeaveConflictError,
    InvalidLeaveStatusTransitionError,
)
from .models import LeaveRequest, LeaveType


# Valid state transitions for leave requests
ALLOWED_TRANSITIONS = {
    'pending': {'approved', 'rejected', 'cancelled'},
    'approved': {'cancelled'},
    'rejected': set(),        # Terminal state
    'cancelled': set(),       # Terminal state
}


class LeaveService:
    """
    Encapsulates all business logic for leave request lifecycle.
    Validates status transitions before committing changes.
    """

    @staticmethod
    def _get_leave(pk: int) -> LeaveRequest:
        try:
            return (
                LeaveRequest.objects
                .with_relations()
                .get(pk=pk)
            )
        except LeaveRequest.DoesNotExist:
            raise LeaveNotFoundError(f"Leave request {pk} not found.")

    @staticmethod
    def _validate_transition(leave: LeaveRequest, target_status: str):
        """Raise InvalidLeaveStatusTransitionError if transition is not allowed."""
        allowed = ALLOWED_TRANSITIONS.get(leave.status, set())
        if target_status not in allowed:
            raise InvalidLeaveStatusTransitionError(leave.status, target_status)

    @staticmethod
    def check_overlapping(employee_id, start_date, end_date,
                          exclude_pk=None) -> bool:
        """
        Check if there's an existing approved/pending leave that overlaps
        with the requested date range.

        Returns:
            bool: True if conflict exists.
        """
        qs = LeaveRequest.objects.filter(
            employee_id=employee_id,
            status__in=['pending', 'approved'],
            start_date__lte=end_date,
            end_date__gte=start_date,
        )
        if exclude_pk:
            qs = qs.exclude(pk=exclude_pk)
        return qs.exists()

    @staticmethod
    @transaction.atomic
    def apply_leave(validated_data: dict) -> LeaveRequest:
        """
        Submit a new leave request with overlap validation.

        Raises:
            LeaveConflictError: If overlapping leave exists.

        Returns:
            LeaveRequest: Newly created instance.
        """
        employee = validated_data.get('employee')
        start_date = validated_data.get('start_date')
        end_date = validated_data.get('end_date')

        if LeaveService.check_overlapping(employee.pk, start_date, end_date):
            raise LeaveConflictError(
                "This employee already has an approved or pending leave "
                "request that overlaps with the requested dates."
            )

        leave = LeaveRequest(**validated_data)
        leave.full_clean()
        leave.save()
        return leave

    @staticmethod
    @transaction.atomic
    def approve_leave(pk: int, reviewer_name: str,
                      note: str = '') -> LeaveRequest:
        """
        Approve a pending leave request.

        Raises:
            InvalidLeaveStatusTransitionError: If leave is not in 'pending' state.
        """
        leave = LeaveService._get_leave(pk)
        LeaveService._validate_transition(leave, 'approved')
        leave.status = 'approved'
        leave.reviewed_by = reviewer_name
        leave.review_note = note
        leave.reviewed_on = timezone.now()
        leave.save(update_fields=[
            'status', 'reviewed_by', 'review_note', 'reviewed_on'
        ])
        return leave

    @staticmethod
    @transaction.atomic
    def reject_leave(pk: int, reviewer_name: str,
                     note: str = '') -> LeaveRequest:
        """
        Reject a pending leave request.

        Raises:
            InvalidLeaveStatusTransitionError: If leave is not in 'pending' state.
        """
        leave = LeaveService._get_leave(pk)
        LeaveService._validate_transition(leave, 'rejected')
        leave.status = 'rejected'
        leave.reviewed_by = reviewer_name
        leave.review_note = note
        leave.reviewed_on = timezone.now()
        leave.save(update_fields=[
            'status', 'reviewed_by', 'review_note', 'reviewed_on'
        ])
        return leave

    @staticmethod
    @transaction.atomic
    def cancel_leave(pk: int) -> LeaveRequest:
        """
        Cancel a pending or approved leave request.

        Raises:
            InvalidLeaveStatusTransitionError: If leave cannot be cancelled.
        """
        leave = LeaveService._get_leave(pk)
        LeaveService._validate_transition(leave, 'cancelled')
        leave.status = 'cancelled'
        leave.save(update_fields=['status'])
        return leave

    @staticmethod
    def get_leave_balance(employee) -> dict:
        """
        Calculate remaining leave balance for an employee.

        Returns:
            dict: {leave_type_name: {'quota': int, 'taken': int, 'remaining': int}}
        """
        approved = (
            LeaveRequest.objects
            .by_status('approved')
            .filter(employee_id=employee.pk, start_date__year=timezone.now().year)
            .select_related('leave_type')
        )
        taken_by_type = {}
        for lr in approved:
            name = lr.leave_type.name if lr.leave_type else 'Unknown'
            taken_by_type[name] = taken_by_type.get(name, 0) + lr.total_days

        leave_types = LeaveType.objects.all()
        balance = {}
        for lt in leave_types:
            taken = taken_by_type.get(lt.name, 0)
            balance[lt.name] = {
                'quota': lt.max_days_per_year,
                'taken': taken,
                'remaining': max(0, lt.max_days_per_year - taken),
            }
        return balance

    @staticmethod
    def get_list(status_filter: str = ''):
        """Return filtered, optimised leave queryset for list view."""
        return (
            LeaveRequest.objects
            .with_relations()
            .by_status(status_filter)
            .ordered()
        )
