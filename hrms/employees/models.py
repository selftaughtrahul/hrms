"""
employees/models.py — Multi-tenant aware Employee and Department models
"""
from django.db import models
from core.models import TenantAwareModel
from .managers import EmployeeManager


class Department(TenantAwareModel):
    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']
        unique_together = ['tenant', 'name']

    def __str__(self):
        return self.name


class Employee(TenantAwareModel):
    EMPLOYEE_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
    ]
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('terminated', 'Terminated'),
    ]

    # Identity
    employee_id = models.CharField(max_length=20, db_index=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(db_index=True)
    phone = models.CharField(max_length=15, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='male')
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)

    # Employment
    employee_type = models.CharField(
        max_length=20, choices=EMPLOYEE_TYPE_CHOICES,
        default='full_time', db_index=True
    )
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='employees'
    )
    designation = models.CharField(max_length=100, blank=True)
    date_of_joining = models.DateField()
    date_of_leaving = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default='active', db_index=True
    )

    # Compensation
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    hourly_rate = models.DecimalField(
        max_digits=8, decimal_places=2, default=0,
        help_text='Applicable for part-time/contract employees'
    )

    # Leave quotas
    annual_leave_quota = models.IntegerField(default=12)
    sick_leave_quota = models.IntegerField(default=6)

    profile_picture = models.ImageField(
        upload_to='employees/', null=True, blank=True
    )

    # Custom manager — replaces default
    objects = EmployeeManager()
    all_objects = models.Manager()  # Bypass manager filters if needed

    class Meta:
        ordering = ['employee_id']
        indexes = [
            models.Index(fields=['employee_type', 'status']),
            models.Index(fields=['department', 'status']),
        ]
        unique_together = [
            ('tenant', 'employee_id'),
            ('tenant', 'email'),
        ]

    def __str__(self):
        return f"{self.employee_id} — {self.get_full_name()}"

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def leaves_taken(self) -> int:
        """Count of approved leave days in the current year."""
        from leaves.models import LeaveRequest
        from datetime import date
        approved = LeaveRequest.objects.filter(
            employee=self,
            status='approved',
            start_date__year=date.today().year,
        )
        return sum(lr.total_days for lr in approved)
