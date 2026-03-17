from django.db import models
from core.models import TimeStampedModel
from employees.models import Employee
from django.utils import timezone

class Attendance(TimeStampedModel):
    STATUS_CHOICES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('half_day', 'Half-Day'),
        ('leave', 'On Leave'),
        ('holiday', 'Holiday'),
    )

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(default=timezone.now, db_index=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='present', db_index=True)
    
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    notes = models.TextField(blank=True, default='')

    class Meta:
        # Enforce exactly one attendance record per employee per day
        unique_together = ['employee', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.date} ({self.get_status_display()})"
