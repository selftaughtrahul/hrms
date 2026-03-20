from django.utils.deprecation import MiddlewareMixin
from core.signals import set_current_user, set_current_tenant


class CurrentUserMiddleware(MiddlewareMixin):
    """
    Captures the logged-in user and saves it to thread-local storage.
    Used by the ActivityLog signals to know who made changes.
    """
    def process_request(self, request):
        if hasattr(request, 'user'):
            set_current_user(request.user)
        else:
            set_current_user(None)

    def process_response(self, request, response):
        set_current_user(None)
        return response


class TenantMiddleware(MiddlewareMixin):
    """
    Resolves the current Tenant from the logged-in user's profile and:
    1. Stores it in thread-local so managers can auto-filter querysets.
    2. Attaches it to `request.tenant` for quick access in views.
    Unauthenticated or superuser requests get tenant=None.
    """
    def process_request(self, request):
        tenant = None
        if hasattr(request, 'user') and request.user.is_authenticated and not request.user.is_superuser:
            try:
                tenant = request.user.profile.tenant
            except Exception:
                tenant = None
        request.tenant = tenant
        set_current_tenant(tenant)

    def process_response(self, request, response):
        set_current_tenant(None)
        return response
