"""
payroll/managers.py
Custom QuerySet and Manager for Payroll model.
"""
from django.db import models
from datetime import date
from core.models import TenantManager


class PayrollQuerySet(models.QuerySet):
    """Chainable queryset methods for Payroll."""

    def for_period(self, month, year):
        return self.filter(month=month, year=year)

    def for_employee(self, employee_id):
        return self.filter(employee_id=employee_id)

    def paid(self):
        return self.filter(status='paid')

    def draft(self):
        return self.filter(status='draft')

    def processed(self):
        return self.filter(status='processed')

    def current_month(self):
        today = date.today()
        return self.for_period(today.month, today.year)

    def with_employee(self):
        """Eager-load employee and department to prevent N+1 queries."""
        return self.select_related('employee', 'employee__department')

    def total_net(self):
        """Return aggregate sum of net salary for this queryset."""
        from django.db.models import Sum
        return self.aggregate(total=Sum('net_salary'))['total'] or 0

    def total_gross(self):
        """Return aggregate sum of gross salary for this queryset."""
        from django.db.models import Sum
        return self.aggregate(total=Sum('gross_salary'))['total'] or 0


class PayrollManager(TenantManager):
    """Inherits global tenant filtering from TenantManager."""

    def get_queryset(self):
        return PayrollQuerySet(self.model, using=self._db).filter(
            pk__in=super().get_queryset().values('pk')
        )

    def for_period(self, month, year):
        return self.get_queryset().for_period(month, year).with_employee()

    def for_employee(self, employee_id):
        return self.get_queryset().for_employee(employee_id)

    def current_month(self):
        return self.get_queryset().current_month().with_employee()

    def get_period_summary(self, month, year):
        """Return aggregated stats for a given pay period."""
        from django.db.models import Count
        qs = self.get_queryset().for_period(month, year)
        return {
            'total_records': qs.count(),
            'total_gross': qs.total_gross(),
            'total_net': qs.total_net(),
            'paid_count': qs.filter(status='paid').count(),
            'draft_count': qs.filter(status='draft').count(),
        }
