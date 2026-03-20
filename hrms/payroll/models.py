"""
payroll/models.py — Multi-tenant aware Payroll model
"""
from django.db import models
from core.models import TenantAwareModel
from .managers import PayrollManager


class Payroll(TenantAwareModel):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('processed', 'Processed'),
        ('paid', 'Paid'),
    ]
    MONTH_CHOICES = [
        (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December'),
    ]

    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='payrolls', db_index=True
    )
    month = models.IntegerField(choices=MONTH_CHOICES, db_index=True)
    year = models.IntegerField(db_index=True)

    # ── Earnings ──────────────────────────────────────────────────────────
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    hra = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='HRA')
    travel_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_allowances = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    overtime_pay = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    hours_worked = models.DecimalField(
        max_digits=8, decimal_places=2, default=0,
        help_text='Applicable for part-time/contract employees'
    )

    # ── Deductions ────────────────────────────────────────────────────────
    pf_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='PF')
    tax_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='TDS')
    other_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    leave_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # ── Net ───────────────────────────────────────────────────────────────
    gross_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # ── Payment ───────────────────────────────────────────────────────────
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default='draft', db_index=True
    )
    payment_date = models.DateField(null=True, blank=True)
    payment_mode = models.CharField(max_length=50, blank=True, default='Bank Transfer')
    notes = models.TextField(blank=True)

    # Custom manager
    objects = PayrollManager()

    class Meta:
        unique_together = ['employee', 'month', 'year']
        ordering = ['-year', '-month']
        indexes = [
            models.Index(fields=['month', 'year', 'status']),
            models.Index(fields=['employee', 'year']),
        ]

    def __str__(self):
        return f"{self.employee.get_full_name()} — {self.get_month_display()} {self.year}"
