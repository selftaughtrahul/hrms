"""
core/models.py
Abstract base models providing common fields for all HRMS models.
"""
from django.db import models


class TimeStampedModel(models.Model):
    """
    Abstract base model providing self-managed `created_at` and `updated_at` fields.
    All HRMS models should inherit from this instead of models.Model directly.
    """
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteManager(models.Manager):
    """Manager that excludes soft-deleted records by default."""
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class SoftDeleteModel(TimeStampedModel):
    """
    Abstract base that adds soft-delete capability.
    Records are marked as deleted rather than physically removed.
    """
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()  # Access including deleted records

    class Meta:
        abstract = True

    def soft_delete(self):
        from django.utils import timezone
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at'])


class ActivityLog(TimeStampedModel):
    """
    Tracks application activity automatically using Django Signals.
    Displayed in the frontend Notification Bell dropdown.
    """
    user = models.ForeignKey(
        'auth.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='activities'
    )
    action = models.CharField(max_length=50) # e.g., 'Created', 'Updated', 'Deleted'
    description = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        usr = self.user.username if self.user else "System"
        return f"{usr} {self.action}: {self.description[:30]}"


class CompanyConfig(TimeStampedModel):
    """
    Singleton model to hold global settings like Company Name and Logo.
    Enforces that only one record (pk=1) ever exists.
    """
    company_name = models.CharField(max_length=150, default='My Company')
    company_address = models.TextField(blank=True, default='')
    company_logo = models.ImageField(upload_to='company_logos/', null=True, blank=True)
    
    # Global Theming
    global_font_family = models.CharField(
        max_length=50, 
        default="'Inter', sans-serif",
        help_text="Standard CSS font-family string (e.g. 'Roboto', sans-serif)"
    )
    global_background_color = models.CharField(
        max_length=20, 
        default="#f4f6f9",
        help_text="Hex color code for the main background (e.g. #f4f6f9)"
    )
    primary_color = models.CharField(
        max_length=20,
        default="#0d6efd",
        help_text="Hex color code for primary accents and buttons (e.g. #0d6efd)"
    )

    # Payroll & Finance
    hra_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=40.00,
        help_text="House Rent Allowance percentage (e.g., 40.00)"
    )
    pf_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=12.00,
        help_text="Provident Fund deduction percentage (e.g., 12.00)"
    )

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass # Prevent deletion of the master config

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    class Meta:
        verbose_name = 'Company Configuration'
        verbose_name_plural = 'Company Configuration'

    def __str__(self):
        return "Master Configuration"

