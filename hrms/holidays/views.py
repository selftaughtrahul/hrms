"""
holidays/views.py
Class-Based Views for Holiday management.
"""
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from datetime import date

from core.mixins import HRMSLoginMixin, HRMSCreateMixin, HRMSUpdateMixin, HRMSDeleteMixin
from .models import Holiday
from .forms import HolidayForm
from .services import HolidayService


class HolidayListView(HRMSLoginMixin, ListView):
    """List holidays filtered by year with type summary."""
    template_name = 'holidays/list.html'
    context_object_name = 'holidays'

    def _get_year(self) -> int:
        try:
            return int(self.request.GET.get('year', date.today().year))
        except (ValueError, TypeError):
            return date.today().year

    def get_queryset(self):
        return HolidayService.get_for_year(self._get_year())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        year = self._get_year()
        type_counts = HolidayService.get_type_summary(year)
        context.update({
            'selected_year': year,
            'years': list(range(date.today().year - 1, date.today().year + 3)),
            'national_count': type_counts.get('national', 0),
            'company_count': type_counts.get('company', 0),
            'regional_count': type_counts.get('regional', 0),
            'optional_count': type_counts.get('optional', 0),
        })
        return context


class HolidayCreateView(HRMSLoginMixin, HRMSCreateMixin, CreateView):
    """Create a holiday."""
    template_name = 'holidays/form.html'
    form_class = HolidayForm
    success_url = reverse_lazy('holiday_list')
    success_message = 'Holiday added successfully!'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Holiday'
        return context


class HolidayUpdateView(HRMSLoginMixin, HRMSUpdateMixin, UpdateView):
    """Update a holiday."""
    template_name = 'holidays/form.html'
    form_class = HolidayForm
    model = Holiday
    success_url = reverse_lazy('holiday_list')
    success_message = 'Holiday updated successfully!'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'title': 'Edit Holiday', 'holiday': self.object})
        return context


class HolidayDeleteView(HRMSLoginMixin, HRMSDeleteMixin, DeleteView):
    """Delete a holiday."""
    template_name = 'holidays/confirm_delete.html'
    model = Holiday
    success_url = reverse_lazy('holiday_list')
    success_message = 'Holiday deleted.'
