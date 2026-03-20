from django.contrib import admin
from .models import ActivityLog, CompanyConfig, Tenant, UserProfile


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'owner_email', 'plan', 'is_active', 'created_at']
    list_filter = ['plan', 'is_active']
    search_fields = ['name', 'slug', 'owner_email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'tenant', 'role', 'created_at']
    list_filter = ['role', 'tenant']
    search_fields = ['user__username', 'user__email', 'tenant__name']
    raw_id_fields = ['user']


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'tenant', 'action', 'created_at']
    list_filter = ['action', 'tenant']
    search_fields = ['user__username', 'description', 'tenant__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(CompanyConfig)
class CompanyConfigAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'tenant', 'plan_display', 'primary_color']
    search_fields = ['company_name', 'tenant__name']
    readonly_fields = ['tenant']

    def plan_display(self, obj):
        if obj.tenant:
            return obj.tenant.get_plan_display()
        return "N/A"
    plan_display.short_description = 'Plan'
