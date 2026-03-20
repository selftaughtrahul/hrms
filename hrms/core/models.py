"""
core/models.py
Abstract base models providing common fields for all HRMS models.
Includes multi-tenant SaaS support via the Tenant model.
"""
from django.db import models
from django.utils.text import slugify
import uuid


class Tenant(models.Model):
    """
    Represents one company/organisation that has signed up for the HRMS SaaS.
    Every piece of data in the system belongs to exactly one Tenant.
    """
    PLAN_CHOICES = [
        ('free', 'Free'),
        ('pro', 'Pro'),
        ('enterprise', 'Enterprise'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150, verbose_name='Company Name')
    slug = models.SlugField(max_length=100, unique=True, db_index=True,
                            help_text='Unique identifier used in URLs')
    owner_email = models.EmailField(unique=True)
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Tenant'
        verbose_name_plural = 'Tenants'

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Tenant.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.slug})"


class TimeStampedModel(models.Model):
    """
    Abstract base model providing self-managed `created_at` and `updated_at` fields.
    All HRMS models should inherit from this instead of models.Model directly.
    """
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class TenantManager(models.Manager):
    """
    Global manager added to every TenantAwareModel.
    Automatically filters querysets to the current tenant stored in
    thread-local by TenantMiddleware.  No per-view or per-model changes needed.
    - Authenticated non-superuser → only sees their own tenant's rows.
    - Superuser / unauthenticated    → sees all rows (admin / migrations / etc.)
    """
    def get_queryset(self):
        from core.signals import get_current_tenant
        qs = super().get_queryset()
        tenant = get_current_tenant()
        if tenant is not None:
            qs = qs.filter(tenant=tenant)
        return qs


class TenantAwareModel(TimeStampedModel):
    """
    Abstract base for all SaaS-aware models.
    Adds a `tenant` FK so every record is scoped to exactly one company.
    The default `objects` manager automatically filters to the current tenant.
    """
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='+',
        db_index=True,
        null=True,   # Allows existing rows to be migrated via assign_default_tenant
        blank=True,
    )

    # ── Global tenant-scoped manager (auto-applied to every subclass) ──────
    objects = TenantManager()
    # Bypass manager: use Model.unscoped.all() if you need all-tenant access
    unscoped = models.Manager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """
        Ensures every record is automatically assigned to the current tenant
        before being saved to the database.
        """
        from core.signals import get_current_tenant
        if not self.tenant:
            tenant = get_current_tenant()
            if tenant:
                self.tenant = (tenant if isinstance(tenant, Tenant) 
                               else Tenant.objects.get(pk=tenant))
        super().save(*args, **kwargs)



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
    Scoped to a tenant so companies only see their own activity.
    """
    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE,
        null=True, blank=True, related_name='activity_logs', db_index=True
    )
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
    Per-tenant company settings (formerly a singleton, now one per Tenant).
    Each company that signs up gets their own CompanyConfig.
    """
    tenant = models.OneToOneField(
        Tenant, on_delete=models.CASCADE,
        related_name='config',
        null=True, blank=True,  # Null for existing pre-SaaS row; populated by assign_default_tenant
    )
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
        max_digits=5, decimal_places=2, default=40.00,
        help_text="House Rent Allowance percentage (e.g., 40.00)"
    )
    pf_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=12.00,
        help_text="Provident Fund deduction percentage (e.g., 12.00)"
    )

    @classmethod
    def load_for_tenant(cls, tenant):
        """Get or create a CompanyConfig for the given tenant."""
        obj, _ = cls.objects.get_or_create(tenant=tenant)
        return obj

    class Meta:
        verbose_name = 'Company Configuration'
        verbose_name_plural = 'Company Configurations'

    def __str__(self):
        return f"Config for {self.tenant.name if self.tenant else 'Unknown Tenant'}"


class UserProfile(models.Model):
    """
    Links a Django auth.User to a Tenant.
    Every user in the system belongs to exactly one company (tenant).
    Role determines what HRMS features they can access.
    """
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('staff', 'Staff'),
    ]

    user = models.OneToOneField(
        'auth.User', on_delete=models.CASCADE, related_name='profile'
    )
    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name='users'
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} @ {self.tenant.name} ({self.role})"

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'


# ── Signals ───────────────────────────────────────────────────────────────────
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender='auth.User')
def create_user_profile(sender, instance, created, **kwargs):
    """Auto-create a UserProfile when a superuser is created via createsuperuser.
    Regular users get a profile created in the signup view with tenant context."""
    if created and instance.is_superuser:
        # Superusers don't belong to any tenant; profile is created downstream
        pass
