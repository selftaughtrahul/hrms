"""
core/views.py
Internal JSON API endpoints for the Realtime Activity Notification polling.
"""
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.timesince import timesince
from django.views.generic import UpdateView
from django.urls import reverse_lazy
from .models import ActivityLog, CompanyConfig
from .mixins import StaffRequiredMixin, HRMSUpdateMixin
from .forms import CompanyConfigForm

class ActivityListAPIView(LoginRequiredMixin, View):
    """Returns the 10 most recent unread activities for the bell icon dropdown."""
    def get(self, request, *args, **kwargs):
        activities = ActivityLog.objects.filter(is_read=False).select_related('user')[:10]
        data = []
        for act in activities:
            data.append({
                'id': act.pk,
                'user': act.user.username if act.user else "System",
                'action': act.action,
                'description': act.description,
                'timesince': f"{timesince(act.created_at)} ago"
            })
        return JsonResponse({'unread_count': ActivityLog.objects.filter(is_read=False).count(), 'activities': data})


class ActivityMarkReadAPIView(LoginRequiredMixin, View):
    """Marks all current unread activities as read."""
    def post(self, request, *args, **kwargs):
        ActivityLog.objects.filter(is_read=False).update(is_read=True)
        return JsonResponse({'status': 'success'})

class CompanyConfigUpdateView(StaffRequiredMixin, HRMSUpdateMixin, UpdateView):
    """
    Global settings page for Admins to change Company Name, Logo, and UI Themes.
    """
    model = CompanyConfig
    form_class = CompanyConfigForm
    template_name = 'core/config_form.html'
    success_url = reverse_lazy('core_settings_global')
    success_message = "Global settings updated successfully! Changes applied immediately."

    def get_object(self, queryset=None):
        return CompanyConfig.load()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = "Global Settings"
        context['page_subtitle'] = "Manage company branding and UI themes"
        return context
