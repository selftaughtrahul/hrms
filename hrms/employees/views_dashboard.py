"""
employees/views_dashboard.py — Refactored to use CBV and service layer
"""
from django.views.generic import TemplateView

from core.mixins import HRMSLoginMixin
from employees.models import Employee
from employees.services import EmployeeService
from leaves.models import LeaveRequest
from holidays.services import HolidayService
from payroll.services import PayrollService
from datetime import date


class DashboardView(HRMSLoginMixin, TemplateView):
    """
    Main dashboard view.
    Aggregates stats from all modules via their respective services.
    No direct model queries here — all delegated to service layer.
    """
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()
        emp_stats = EmployeeService.get_dashboard_stats()
        payroll_summary = PayrollService.get_monthly_summary(today.month, today.year)
        leave_counts = LeaveRequest.objects.get_status_counts()

        context.update({
            # Employee stats
            'total_employees': emp_stats['total'],
            'full_time_count': emp_stats['full_time'],
            'part_time_count': emp_stats['part_time'],
            'contract_count': emp_stats['contract'],
            # Leave stats
            'pending_leaves': leave_counts.get('pending', 0),
            # Payroll stats
            'current_payroll': payroll_summary['total_records'],
            'paid_payrolls': payroll_summary['paid_count'],
            # Lists
            'upcoming_holidays': HolidayService.get_upcoming(limit=5),
            'recent_employees': (
                Employee.objects.with_relations().active()
                .order_by('-created_at')[:5]
            ),
            'recent_leaves': (
                LeaveRequest.objects.with_relations().ordered()[:5]
            ),
            'today': today,
        })
        return context
