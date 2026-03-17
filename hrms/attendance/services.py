from datetime import date, datetime
from django.utils import timezone
from .models import Attendance
from employees.models import Employee

class AttendanceService:
    @staticmethod
    def punch_in(employee_id, notes=""):
        """Logs the employee's check-in time for today."""
        today = timezone.localdate()
        attendance, created = Attendance.objects.get_or_create(
            employee_id=employee_id,
            date=today,
            defaults={'check_in': timezone.localtime().time(), 'status': 'present', 'notes': notes}
        )
        if not created and not attendance.check_in:
            attendance.check_in = timezone.localtime().time()
            attendance.status = 'present'
            if notes:
                attendance.notes += f"\nPunch In: {notes}"
            attendance.save(update_fields=['check_in', 'status', 'notes'])
        return attendance

    @staticmethod
    def punch_out(employee_id, notes=""):
        """Logs the employee's check-out time for today."""
        today = timezone.localdate()
        attendance = Attendance.objects.filter(employee_id=employee_id, date=today).first()
        if attendance:
            attendance.check_out = timezone.localtime().time()
            if notes:
                attendance.notes += f"\nPunch Out: {notes}"
            attendance.save(update_fields=['check_out', 'notes'])
        else:
            # Pushed out without checking in -> irregular record
            attendance = Attendance.objects.create(
                employee_id=employee_id,
                date=today,
                check_out=timezone.localtime().time(),
                status='half_day',
                notes=f"Punched out without punch in. Note: {notes}"
            )
        return attendance

    @staticmethod
    def get_monthly_summary(employee_id, month, year):
        """
        Returns a dictionary grouping the number of days Present, Absent, Half-Day, etc.
        Used heavily by the PayrollService to calculate deductions.
        """
        records = Attendance.objects.filter(
            employee_id=employee_id, 
            date__year=year, 
            date__month=month
        )
        
        summary = {
            'present': 0, 'absent': 0, 'half_day': 0, 'leave': 0, 'holiday': 0
        }
        for r in records:
            if r.status in summary:
                summary[r.status] += 1
                
        # Calculate unpaid days (Absent = 1, Half-Day = 0.5)
        unpaid_days = summary['absent'] + (summary['half_day'] * 0.5)
        summary['total_unpaid_days'] = unpaid_days
        summary['total_logged_days'] = records.count()
        
        return summary
