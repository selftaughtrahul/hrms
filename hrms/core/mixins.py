"""
core/mixins.py
Reusable Class-Based View mixins for security, messaging, and DRY behaviour.
All HRMS views should compose from these mixins rather than repeating logic.
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View


# ─── Security Mixins ─────────────────────────────────────────────────────────

class HRMSLoginMixin(LoginRequiredMixin):
    """
    Extends Django's LoginRequiredMixin.
    - Enforces authentication on every HRMS view.
    - Adds a user-friendly flash message on redirect.
    """
    login_url = '/login/'
    redirect_field_name = 'next'

    def handle_no_permission(self):
        messages.warning(
            self.request,
            'Please log in to access this page.'
        )
        return super().handle_no_permission()


class StaffRequiredMixin(HRMSLoginMixin):
    """Restricts access to staff/admin users only."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return HttpResponseForbidden(
                'You do not have permission to access this resource.'
            )
        return super().dispatch(request, *args, **kwargs)


# ─── Message Mixins ──────────────────────────────────────────────────────────

class HRMSCreateMixin:
    """
    Mixin for CreateView that adds a success message after object creation.
    Override `get_success_message()` to customise.
    """
    success_message: str = 'Record created successfully!'

    def get_success_message(self, obj) -> str:
        return self.success_message

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, self.get_success_message(self.object))
        return response


class HRMSUpdateMixin:
    """
    Mixin for UpdateView that adds a success message after updating an object.
    """
    success_message: str = 'Record updated successfully!'

    def get_success_message(self, obj) -> str:
        return self.success_message

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, self.get_success_message(self.object))
        return response


class HRMSDeleteMixin:
    """
    Mixin for DeleteView that:
    - Restricts deletion to POST requests only (CSRF-safe)
    - Adds a success message after deletion
    """
    success_message: str = 'Record deleted successfully.'
    cancel_url: str = '/'

    def get_success_message(self) -> str:
        return self.success_message

    def delete(self, request, *args, **kwargs):
        messages.success(request, self.get_success_message())
        return super().delete(request, *args, **kwargs)


# ─── Context Mixins ──────────────────────────────────────────────────────────

class HRMSContextMixin:
    """
    Injects common template context variables available to every view:
    - page_title
    - page_subtitle
    Override in each view as needed.
    """
    page_title: str = 'HRMS'
    page_subtitle: str = ''

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        context['page_subtitle'] = self.page_subtitle
        return context
