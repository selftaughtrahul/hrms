"""
leaves/models.py — Refactored to use TimeStampedModel and LeaveManager
"""
from django.db import models
from core.models import TimeStampedModel
from .managers import LeaveManager


class LeaveType(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    max_days_per_year = models.IntegerField(default=10)
    is_paid = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class LeaveRequest(TimeStampedModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]

    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='leave_requests', db_index=True
    )
    leave_type = models.ForeignKey(
        LeaveType, on_delete=models.SET_NULL,
        null=True, related_name='requests'
    )
    start_date = models.DateField(db_index=True)
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default='pending', db_index=True
    )
    applied_on = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.CharField(max_length=100, blank=True)
    review_note = models.TextField(blank=True)
    reviewed_on = models.DateTimeField(null=True, blank=True)

    # Custom manager
    objects = LeaveManager()

    class Meta:
        ordering = ['-applied_on']
        indexes = [
            models.Index(fields=['employee', 'status']),
            models.Index(fields=['start_date', 'end_date']),
        ]

    def __str__(self):
        return (
            f"{self.employee.get_full_name()} — "
            f"{self.leave_type} ({self.start_date} → {self.end_date})"
        )

    @property
    def total_days(self) -> int:
        """Total calendar days for this leave request."""
        return (self.end_date - self.start_date).days + 1
