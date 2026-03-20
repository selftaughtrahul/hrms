"""
employees/views.py
Class-Based Views for Employee and Department management.
All views enforce authentication via HRMSLoginMixin.
Business logic delegated to EmployeeService / DepartmentService.
"""
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect

from django.http import Http404
from core.mixins import HRMSLoginMixin, HRMSCreateMixin, HRMSUpdateMixin, HRMSDeleteMixin
from core.exceptions import DuplicateEmployeeIDError, EmployeeNotFoundError

from .models import Employee, Department
from .forms import EmployeeForm, DepartmentForm
from .services import EmployeeService, DepartmentService


# ─── Employee Views ───────────────────────────────────────────────────────────

class EmployeeListView(HRMSLoginMixin, ListView):
    """
    Displays a filterable, searchable list of employees.
    Delegates all query logic to EmployeeService.
    """
    template_name = 'employees/list.html'
    context_object_name = 'employees'
    paginate_by = 20

    def get_queryset(self):
        return EmployeeService.get_filtered_list(
            query=self.request.GET.get('q', ''),
            emp_type=self.request.GET.get('type', ''),
            department_id=self.request.GET.get('department', ''),
            status=self.request.GET.get('status', ''),
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        context.update({
            'departments': DepartmentService.get_all(),
            'total': qs.count(),
            'full_time': qs.filter(employee_type='full_time').count(),
            'part_time': qs.filter(employee_type='part_time').count(),
            'contract': qs.filter(employee_type='contract').count(),
        })
        return context


class EmployeeDetailView(HRMSLoginMixin, DetailView):
    """Displays an employee profile with leave history and payroll summary."""
    template_name = 'employees/detail.html'
    context_object_name = 'employee'

    def get_object(self, queryset=None):
        try:
            return EmployeeService.get_employee(pk=self.kwargs['pk'])
        except EmployeeNotFoundError:
            raise Http404("Employee not found or access denied.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee = self.object
        context['leave_requests'] = (
            employee.leave_requests
            .select_related('leave_type')
            .order_by('-applied_on')[:5]
        )
        context['payrolls'] = (
            employee.payrolls
            .order_by('-year', '-month')[:6]
        )
        return context


class EmployeeCreateView(HRMSLoginMixin, HRMSCreateMixin, CreateView):
    """Create a new employee record via form."""
    template_name = 'employees/form.html'
    form_class = EmployeeForm
    success_message = 'Employee created successfully!'

    def get_success_url(self):
        return reverse_lazy('employee_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'title': 'Add Employee', 'action': 'Create'})
        return context

    def form_valid(self, form):
        # Service now only used for complex business logic if needed.
        # Unique ID validation is handled by the model's unique_together constraint.
        return super().form_valid(form)


class EmployeeUpdateView(HRMSLoginMixin, HRMSUpdateMixin, UpdateView):
    """Update an existing employee record."""
    template_name = 'employees/form.html'
    form_class = EmployeeForm
    success_message = 'Employee updated successfully!'
    queryset = Employee.objects.with_relations()

    def get_success_url(self):
        return reverse_lazy('employee_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Edit Employee',
            'action': 'Update',
            'employee': self.object,
        })
        return context


class EmployeeDeleteView(HRMSLoginMixin, HRMSDeleteMixin, DeleteView):
    """Delete an employee record with confirmation."""
    template_name = 'employees/confirm_delete.html'
    model = Employee
    success_url = reverse_lazy('employee_list')

    def get_success_message(self):
        return f'Employee {self.object.get_full_name()} deleted successfully.'


# ─── Department Views ─────────────────────────────────────────────────────────

class DepartmentListView(HRMSLoginMixin, ListView):
    """List all departments."""
    template_name = 'employees/departments.html'
    context_object_name = 'departments'

    def get_queryset(self):
        return DepartmentService.get_all()


class DepartmentCreateView(HRMSLoginMixin, HRMSCreateMixin, CreateView):
    """Create a new department."""
    template_name = 'employees/dept_form.html'
    form_class = DepartmentForm
    success_url = reverse_lazy('department_list')
    success_message = 'Department created successfully!'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Department'
        return context


class DepartmentUpdateView(HRMSLoginMixin, HRMSUpdateMixin, UpdateView):
    """Update a department."""
    template_name = 'employees/dept_form.html'
    form_class = DepartmentForm
    model = Department
    success_url = reverse_lazy('department_list')
    success_message = 'Department updated successfully!'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'title': 'Edit Department', 'dept': self.object})
        return context


class DepartmentDeleteView(HRMSLoginMixin, HRMSDeleteMixin, DeleteView):
    """Delete a department."""
    template_name = 'employees/dept_confirm_delete.html'
    model = Department
    success_url = reverse_lazy('department_list')
    success_message = 'Department deleted.'
