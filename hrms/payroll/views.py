"""
payroll/views.py
Class-Based Views for Payroll management.
Business logic delegated entirely to PayrollService.
"""
from datetime import date
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View, View
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse

from core.mixins import HRMSLoginMixin, HRMSCreateMixin, HRMSUpdateMixin, HRMSDeleteMixin
from core.exceptions import PayrollAlreadyExistsError, InvalidPayrollStateError
from core.pdf_utils import render_to_pdf

from .models import Payroll
from .forms import PayrollForm
from .services import PayrollService
from employees.models import Employee


class PayrollListView(HRMSLoginMixin, ListView):
    """
    Display payroll records for a given month/year with summary totals.
    All query optimisation handled by PayrollService.
    """
    template_name = 'payroll/list.html'
    context_object_name = 'payrolls'

    def _get_period(self):
        today = date.today()
        try:
            month = int(self.request.GET.get('month', today.month))
            year = int(self.request.GET.get('year', today.year))
        except (ValueError, TypeError):
            month, year = today.month, today.year
        return month, year

    def get_queryset(self):
        month, year = self._get_period()
        return PayrollService.get_period_list(month, year)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        month, year = self._get_period()
        summary = PayrollService.get_monthly_summary(month, year)
        context.update({
            'selected_month': month,
            'selected_year': year,
            'years': list(range(date.today().year - 2, date.today().year + 2)),
            'months': Payroll.MONTH_CHOICES,
            **summary,
        })
        return context


class PayrollDetailView(HRMSLoginMixin, DetailView):
    """Detailed view of a single payroll record."""
    template_name = 'payroll/detail.html'
    context_object_name = 'payroll'
    queryset = Payroll.objects.select_related('employee', 'employee__department')


class PayrollCreateView(HRMSLoginMixin, CreateView):
    """
    Create a new payroll record, auto-calculates gross and net via service.
    Pre-fills form from employee profile if `?employee=<id>` is provided.
    """
    template_name = 'payroll/form.html'
    form_class = PayrollForm

    def get_success_url(self):
        return reverse_lazy('payroll_detail', kwargs={'pk': self.object.pk})

    def get_initial(self):
        initial = super().get_initial()
        employee_id = self.request.GET.get('employee')
        if employee_id:
            try:
                emp = Employee.objects.get(pk=employee_id)
                initial.update(PayrollService.prefill_from_employee(emp))
            except Employee.DoesNotExist:
                pass
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Payroll'
        return context

    def form_valid(self, form):
        try:
            self.object = PayrollService.create_payroll(form.cleaned_data)
            messages.success(self.request, 'Payroll created and calculated successfully!')
            return redirect(self.get_success_url())
        except PayrollAlreadyExistsError as exc:
            form.add_error(None, str(exc))
            return self.form_invalid(form)


class PayrollUpdateView(HRMSLoginMixin, UpdateView):
    """
    Update a payroll record and recalculate totals.
    Blocked if payroll is already marked as 'paid'.
    """
    template_name = 'payroll/form.html'
    form_class = PayrollForm
    model = Payroll

    def get_success_url(self):
        return reverse_lazy('payroll_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'title': 'Edit Payroll', 'payroll': self.object})
        return context

    def form_valid(self, form):
        try:
            self.object = PayrollService.update_payroll(
                self.object.pk, form.cleaned_data
            )
            messages.success(self.request, 'Payroll updated successfully!')
            return redirect(self.get_success_url())
        except (PayrollAlreadyExistsError, InvalidPayrollStateError) as exc:
            form.add_error(None, str(exc))
            return self.form_invalid(form)


class PayrollDeleteView(HRMSLoginMixin, HRMSDeleteMixin, DeleteView):
    """Delete a payroll record."""
    template_name = 'payroll/confirm_delete.html'
    model = Payroll
    success_url = reverse_lazy('payroll_list')
    success_message = 'Payroll record deleted.'


class PayrollMarkPaidView(HRMSLoginMixin, View):
    """POST-only view to transition a payroll record to 'paid' status."""
    http_method_names = ['post']

    def post(self, request, pk):
        try:
            PayrollService.mark_as_paid(pk)
            messages.success(request, 'Payroll marked as paid!')
        except InvalidPayrollStateError as exc:
            messages.error(request, str(exc))
        return redirect('payroll_detail', pk=pk)


class PayslipView(HRMSLoginMixin, DetailView):
    """Printable payslip view for an employee's payroll record."""
    template_name = 'payroll/payslip.html'
    context_object_name = 'payroll'
    queryset = Payroll.objects.select_related('employee', 'employee__department')

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        
        if request.GET.get('download') == 'pdf':
            pdf = render_to_pdf(self.template_name, context)
            if pdf:
                response = pdf
                filename = f"Payslip_{self.object.employee.employee_id}_{self.object.get_month_display()}_{self.object.year}.pdf"
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response
            return HttpResponse("Error Rendering PDF", status=400)
            
        return super().get(request, *args, **kwargs)


class CalculatePayrollAPIView(HRMSLoginMixin, View):
    """
    AJAX endpoint returning pre-calculated salary breakdowns for an Employee.
    Takes employee_id, month, and year as GET parameters.
    """
    def get(self, request, *args, **kwargs):
        employee_id = request.GET.get('employee_id')
        month = request.GET.get('month')
        year = request.GET.get('year')
        
        try:
            employee = Employee.objects.get(pk=employee_id)
        except (ValueError, TypeError, Employee.DoesNotExist):
            return JsonResponse({'error': 'Invalid or missing employee ID'}, status=400)
            
        try:
            # Cast month and year if available
            m_val = int(month) if month else None
            y_val = int(year)  if year  else None
            
            data = PayrollService.prefill_from_employee(employee, month=m_val, year=y_val)
            # Remove complex objects before returning JSON
            data.pop('employee', None)
            return JsonResponse(data)
        except ValueError as e:
            # This triggers if a future date is provided
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
