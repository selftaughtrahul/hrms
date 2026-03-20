"""
leaves/managers.py
Custom QuerySet and Manager for LeaveRequest model.
"""
from django.db import models
from core.models import TenantManager


class LeaveQuerySet(models.QuerySet):
    """Chainable queryset methods for LeaveRequest."""

    def pending(self):
        return self.filter(status='pending')

    def approved(self):
        return self.filter(status='approved')

    def rejected(self):
        return self.filter(status='rejected')

    def cancelled(self):
        return self.filter(status='cancelled')

    def for_employee(self, employee_id):
        return self.filter(employee_id=employee_id)

    def current_year(self):
        from datetime import date
        return self.filter(start_date__year=date.today().year)

    def by_status(self, status):
        if status:
            return self.filter(status=status)
        return self

    def with_relations(self):
        """Eager-load employee and leave_type to prevent N+1."""
        return self.select_related(
            'employee',
            'employee__department',
            'leave_type'
        )

    def ordered(self):
        return self.order_by('-applied_on')


class LeaveManager(TenantManager):
    """Inherits global tenant filtering from TenantManager."""

    def get_queryset(self):
        return LeaveQuerySet(self.model, using=self._db).filter(
            pk__in=super().get_queryset().values('pk')
        )

    def pending(self):
        return self.get_queryset().pending()

    def for_employee(self, employee_id):
        return self.get_queryset().for_employee(employee_id)

    def by_status(self, status):
        return self.get_queryset().by_status(status)

    def with_relations(self):
        return self.get_queryset().with_relations()

    def get_status_counts(self):
        """Return a dict of counts grouped by status."""
        from django.db.models import Count
        rows = self.get_queryset().values('status').annotate(total=Count('id'))
        return {r['status']: r['total'] for r in rows}
