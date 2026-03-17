"""
holidays/services.py
Business logic layer for Holiday management.
"""
from django.db import transaction
from .models import Holiday


class HolidayService:
    """Encapsulates business logic for holiday management."""

    @staticmethod
    def get_for_year(year: int):
        """Return all holidays for the given year, ordered by date."""
        return Holiday.objects.for_year(year).order_by('date')

    @staticmethod
    def get_upcoming(limit: int = 5):
        """Return the next N upcoming holidays."""
        return Holiday.objects.upcoming(limit=limit)

    @staticmethod
    def get_type_summary(year: int) -> dict:
        """
        Return counts of each holiday type for a year.

        Returns:
            dict: {'national': N, 'company': N, ...}
        """
        return Holiday.objects.get_type_counts(year)

    @staticmethod
    @transaction.atomic
    def create_holiday(validated_data: dict) -> Holiday:
        """Create a new holiday. Year is auto-set from date in model.save()."""
        holiday = Holiday(**validated_data)
        holiday.full_clean()
        holiday.save()
        return holiday

    @staticmethod
    @transaction.atomic
    def update_holiday(pk: int, validated_data: dict) -> Holiday:
        """Update an existing holiday record."""
        from django.shortcuts import get_object_or_404
        holiday = get_object_or_404(Holiday, pk=pk)
        for field, value in validated_data.items():
            setattr(holiday, field, value)
        holiday.full_clean()
        holiday.save()
        return holiday
