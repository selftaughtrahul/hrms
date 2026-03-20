"""
holidays/models.py — Multi-tenant aware Holiday model
"""
from django.db import models
from core.models import TenantAwareModel
from .managers import HolidayManager


class Holiday(TenantAwareModel):
    HOLIDAY_TYPE_CHOICES = [
        ('national', 'National Holiday'),
        ('regional', 'Regional Holiday'),
        ('company', 'Company Holiday'),
        ('optional', 'Optional Holiday'),
    ]

    name = models.CharField(max_length=200)
    date = models.DateField(db_index=True)
    holiday_type = models.CharField(
        max_length=20, choices=HOLIDAY_TYPE_CHOICES,
        default='national', db_index=True
    )
    description = models.TextField(blank=True)
    is_restricted = models.BooleanField(
        default=False,
        help_text='Mark as optional/restricted holiday'
    )
    year = models.IntegerField(db_index=True, blank=True, null=True)

    # Custom manager
    objects = HolidayManager()

    class Meta:
        ordering = ['date']
        indexes = [
            models.Index(fields=['year', 'holiday_type']),
        ]
        unique_together = ['tenant', 'date']

    def __str__(self):
        return f"{self.name} ({self.date})"

    def clean(self):
        """Auto-derive year from date field before validation."""
        super().clean()
        if self.date:
            self.year = self.date.year

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
