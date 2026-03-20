"""
core/management/commands/assign_default_tenant.py

Management command to migrate all existing single-tenant data to a default Tenant.
Run this ONCE after applying the SaaS multi-tenancy migrations.

Usage:
    python manage.py assign_default_tenant
"""
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = ('Assigns all existing records (employees, payroll, etc.) to a '
            'default Tenant. Run once after the SaaS migration.')

    def handle(self, *args, **options):
        from core.models import Tenant, UserProfile, CompanyConfig
        from employees.models import Employee, Department
        from leaves.models import LeaveType, LeaveRequest
        from holidays.models import Holiday
        from payroll.models import Payroll
        from attendance.models import Attendance
        from django.contrib.auth.models import User

        self.stdout.write(self.style.MIGRATE_HEADING('=== HRMS SaaS: Assign Default Tenant ==='))

        with transaction.atomic():
            # 1. Get or create the default tenant
            tenant, created = Tenant.objects.get_or_create(
                slug='default',
                defaults={
                    'name': 'Default Company',
                    'owner_email': 'admin@default.local',
                    'plan': 'pro',
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  Created default tenant: {tenant}'))
            else:
                self.stdout.write(f'  Using existing default tenant: {tenant}')

            # 2. Create or update CompanyConfig for the default tenant
            cfg, _ = CompanyConfig.objects.get_or_create(tenant=tenant)
            self.stdout.write(f'  CompanyConfig: {cfg}')

            # 3. Assign all records without a tenant to the default tenant
            models_to_migrate = [
                ('Department', Department),
                ('Employee', Employee),
                ('LeaveType', LeaveType),
                ('LeaveRequest', LeaveRequest),
                ('Holiday', Holiday),
                ('Payroll', Payroll),
                ('Attendance', Attendance),
            ]

            for label, Model in models_to_migrate:
                count = Model.objects.filter(tenant__isnull=True).count()
                if count:
                    Model.objects.filter(tenant__isnull=True).update(tenant=tenant)
                    self.stdout.write(self.style.SUCCESS(
                        f'  Migrated {count} {label} records to default tenant.'
                    ))
                else:
                    self.stdout.write(f'  {label}: all records already have a tenant.')

            # 4. Assign all Django users (without a profile) to the default tenant
            users_without_profile = User.objects.filter(profile__isnull=True)
            count = users_without_profile.count()
            if count:
                for user in users_without_profile:
                    role = 'owner' if user.is_staff or user.is_superuser else 'staff'
                    UserProfile.objects.create(user=user, tenant=tenant, role=role)
                self.stdout.write(self.style.SUCCESS(
                    f'  Created UserProfile for {count} existing user(s) → default tenant.'
                ))
            else:
                self.stdout.write('  All users already have a UserProfile.')

        self.stdout.write(self.style.SUCCESS('\nDone! All existing data is now under the default tenant.'))
        self.stdout.write(self.style.WARNING(
            '\nIMPORTANT: Log in to /admin/ and update the default tenant\'s name and owner_email '
            'to match your actual company details.'
        ))
