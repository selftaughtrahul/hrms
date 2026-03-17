from django.utils.deprecation import MiddlewareMixin
from core.signals import set_current_user

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
