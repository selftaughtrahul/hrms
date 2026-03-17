from django.contrib import admin
from .models import ActivityLog, CompanyConfig

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'created_at']
    list_filter = ['action']
    search_fields = ['user__username', 'description']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(CompanyConfig)
class CompanyConfigAdmin(admin.ModelAdmin):
    list_display = ('company_name',)

    def has_add_permission(self, request):
        """Prevent adding multiple rows, force singleton."""
        if self.model.objects.count() >= 1:
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion to enforce singleton."""
        return False
