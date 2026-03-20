"""
employees/managers.py
Custom QuerySet and Manager for the Employee model.
Centralises all employee query logic with built-in optimisation.
"""
from django.db import models
from core.models import TenantManager


class EmployeeQuerySet(models.QuerySet):
    """
    Chainable queryset methods for Employee.
    Usage: Employee.objects.active().full_time().with_relations()
    """

    def active(self):
        """Return only active employees."""
        return self.filter(status='active')

    def inactive(self):
        """Return inactive or terminated employees."""
        return self.exclude(status='active')

    def full_time(self):
        """Filter to full-time employees."""
        return self.filter(employee_type='full_time')

    def part_time(self):
        """Filter to part-time employees."""
        return self.filter(employee_type='part_time')

    def contract(self):
        """Filter to contract employees."""
        return self.filter(employee_type='contract')

    def by_department(self, department_id):
        """Filter by department primary key."""
        return self.filter(department_id=department_id)

    def by_type(self, employee_type):
        """Filter by employee type string."""
        if employee_type:
            return self.filter(employee_type=employee_type)
        return self

    def search(self, query):
        """
        Full-text search across name, email, ID and designation.
        Uses Q objects with OR logic.
        """
        from django.db.models import Q
        if not query:
            return self
        return self.filter(
            Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(email__icontains=query)
            | Q(employee_id__icontains=query)
            | Q(designation__icontains=query)
        )

    def with_relations(self):
        """
        Pre-fetch all related objects to avoid N+1 queries.
        Always use this in list/detail views.
        """
        return self.select_related('department')

    def type_summary(self):
        """
        Return aggregated counts by employee type.
        Returns a dict: {'full_time': N, 'part_time': N, 'contract': N}
        """
        from django.db.models import Count
        counts = self.values('employee_type').annotate(total=Count('id'))
        return {row['employee_type']: row['total'] for row in counts}


class EmployeeManager(TenantManager):
    """
    Manager for Employee. Inherits global tenant filtering from TenantManager.
    Provides chainable helpers via EmployeeQuerySet.
    """

    def get_queryset(self):
        tenant_qs = super().get_queryset()  # applies tenant filter from TenantManager
        # Wrap in EmployeeQuerySet to expose chained helper methods
        return EmployeeQuerySet(self.model, using=self._db).filter(
            pk__in=tenant_qs.values('pk')
        )

    # ─── Convenience proxy methods ─────────────────────────────────────────
    def active(self):
        return self.get_queryset().active()

    def full_time(self):
        return self.get_queryset().full_time()

    def part_time(self):
        return self.get_queryset().part_time()

    def contract(self):
        return self.get_queryset().contract()

    def search(self, query):
        return self.get_queryset().search(query)

    def with_relations(self):
        return self.get_queryset().with_relations()

    def get_stats(self):
        """Return a stats dict of active employee counts by type."""
        qs = self.get_queryset().active()
        return {
            'total': qs.count(),
            'full_time': qs.filter(employee_type='full_time').count(),
            'part_time': qs.filter(employee_type='part_time').count(),
            'contract': qs.filter(employee_type='contract').count(),
        }
