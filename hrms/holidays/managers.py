"""
holidays/managers.py
Custom QuerySet and Manager for Holiday model.
"""
from django.db import models
from datetime import date


class HolidayQuerySet(models.QuerySet):
    """Chainable queryset methods for Holiday."""

    def for_year(self, year=None):
        year = year or date.today().year
        return self.filter(year=year)

    def upcoming(self, limit=5):
        """Return the next N upcoming holidays from today."""
        return (
            self.filter(date__gte=date.today())
            .order_by('date')[:limit]
        )

    def by_type(self, holiday_type):
        if holiday_type:
            return self.filter(holiday_type=holiday_type)
        return self

    def national(self):
        return self.filter(holiday_type='national')

    def company(self):
        return self.filter(holiday_type='company')


class HolidayManager(models.Manager):
    def get_queryset(self):
        return HolidayQuerySet(self.model, using=self._db)

    def for_year(self, year=None):
        return self.get_queryset().for_year(year)

    def upcoming(self, limit=5):
        return self.get_queryset().upcoming(limit)

    def get_type_counts(self, year=None):
        """Return counts of holidays grouped by type for a given year."""
        from django.db.models import Count
        qs = self.get_queryset().for_year(year)
        rows = qs.values('holiday_type').annotate(total=Count('id'))
        return {r['holiday_type']: r['total'] for r in rows}
