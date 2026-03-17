from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import threading

from django.contrib.auth import get_user_model
from core.models import ActivityLog
from employees.models import Employee, Department
from leaves.models import LeaveRequest
from holidays.models import Holiday
from payroll.models import Payroll

# Thread-local storage to capture the user making the request from middleware
_thread_locals = threading.local()

def set_current_user(user):
    _thread_locals.user = user

def get_current_user():
    return getattr(_thread_locals, 'user', None)

def create_activity(action, description):
    user = get_current_user()
    if user and user.is_authenticated:
        ActivityLog.objects.create(user=user, action=action, description=description)
    else:
        ActivityLog.objects.create(action=action, description=description)

@receiver(post_save, sender=Employee)
def log_employee_save(sender, instance, created, **kwargs):
    action = "Created" if created else "Updated"
    create_activity(action, f"Employee {instance.get_full_name()} ({instance.employee_id})")

@receiver(post_delete, sender=Employee)
def log_employee_delete(sender, instance, **kwargs):
    create_activity("Deleted", f"Employee {instance.get_full_name()} ({instance.employee_id})")

@receiver(post_save, sender=LeaveRequest)
def log_leave_save(sender, instance, created, **kwargs):
    action = "Applied For" if created else f"Status changed to {instance.status} for"
    create_activity(action, f"Leave: {instance.employee.get_full_name()}")

@receiver(post_save, sender=Payroll)
def log_payroll_save(sender, instance, created, **kwargs):
    action = "Generated" if created else f"Updated ({instance.status})"
    create_activity(action, f"Payroll for {instance.employee.get_full_name()} ({instance.get_month_display()} {instance.year})")

@receiver(post_save, sender=Holiday)
def log_holiday_save(sender, instance, created, **kwargs):
    action = "Added" if created else "Updated"
    create_activity(action, f"Holiday: {instance.name} ({instance.date})")
