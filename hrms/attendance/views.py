from django.views.generic import ListView, View, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone

from core.mixins import HRMSLoginMixin, StaffRequiredMixin, HRMSCreateMixin, HRMSUpdateMixin, HRMSDeleteMixin
from employees.models import Employee
from .models import Attendance
from .services import AttendanceService
from .forms import AttendanceForm

class AttendanceRecordView(HRMSLoginMixin, ListView):
    """
    Employee-facing view to see their own attendance history 
    and Punch In/Out for the day.
    """
    template_name = 'attendance/record.html'
    context_object_name = 'attendances'

    def get_queryset(self):
        # Match employee profile by email
        employee = Employee.objects.filter(email=self.request.user.email).first()
        if employee:
            return Attendance.objects.filter(employee=employee)[:30]
        return Attendance.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee = Employee.objects.filter(email=self.request.user.email).first()
        
        today = timezone.localdate()
        today_record = None
        if employee:
            today_record = Attendance.objects.filter(
                employee=employee, 
                date=today
            ).first()

        can_punch_in = not today_record or not today_record.check_in
        can_punch_out = today_record and today_record.check_in and not today_record.check_out

        # Disable punching if user is not linked to an employee profile (e.g. system admins)
        if not employee:
            can_punch_in = False
            can_punch_out = False

        context.update({
            'today_record': today_record,
            'can_punch_in': can_punch_in,
            'can_punch_out': can_punch_out,
            'has_employee_profile': bool(employee)
        })
        return context

class PunchInView(HRMSLoginMixin, View):
    http_method_names = ['post']
    def post(self, request, *args, **kwargs):
        # Match employee profile by email
        employee = Employee.objects.filter(email=request.user.email).first()
        if employee:
            AttendanceService.punch_in(employee.pk, notes="Web Punch-In")
            messages.success(request, 'Successfully Punched In for the day.')
        else:
            messages.error(request, 'Your user account is not linked to an Employee record.')
        return redirect('attendance_record')

class PunchOutView(HRMSLoginMixin, View):
    http_method_names = ['post']
    def post(self, request, *args, **kwargs):
        employee = Employee.objects.filter(email=request.user.email).first()
        if employee:
            AttendanceService.punch_out(employee.pk, notes="Web Punch-Out")
            messages.success(request, 'Successfully Punched Out. Have a good evening!')
        else:
            messages.error(request, 'Your user account is not linked to an Employee record.')
        return redirect('attendance_record')

# --- Admin Views ---

class AttendanceAdminListView(StaffRequiredMixin, ListView):
    """Admin view to see all employee attendances."""
    template_name = 'attendance/admin_list.html'
    context_object_name = 'attendances'
    def get_queryset(self):
        return Attendance.objects.select_related('employee').all()
    paginate_by = 20

class AttendanceCreateView(StaffRequiredMixin, HRMSCreateMixin, CreateView):
    """Admin view to manually log attendance for an employee."""
    model = Attendance
    form_class = AttendanceForm
    template_name = 'attendance/form.html'
    success_url = reverse_lazy('attendance_manage_list')
    success_message = "Attendance record created successfully."

class AttendanceUpdateView(StaffRequiredMixin, HRMSUpdateMixin, UpdateView):
    """Admin view to explicitly update an existing attendance record."""
    model = Attendance
    form_class = AttendanceForm
    template_name = 'attendance/form.html'
    success_url = reverse_lazy('attendance_manage_list')
    success_message = "Attendance record updated successfully."

class AttendanceDeleteView(StaffRequiredMixin, HRMSDeleteMixin, DeleteView):
    """Admin view to delete a wrongly created attendance record."""
    model = Attendance
    success_url = reverse_lazy('attendance_manage_list')
    success_message = "Attendance record deleted successfully."
