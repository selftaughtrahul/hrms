"""
Seed script to create initial data for HRMS demo.
Run: python manage.py shell < seed_data.py
"""
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms_project.settings')
django.setup()

from django.contrib.auth.models import User
from employees.models import Employee, Department
from leaves.models import LeaveType
from holidays.models import Holiday
from datetime import date

# Create superuser
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@hrms.com', 'admin123')
    print("Superuser created: admin / admin123")

# Create departments
depts = ['Engineering', 'Human Resources', 'Finance', 'Sales & Marketing', 'Operations']
dept_objs = []
for d in depts:
    obj, _ = Department.objects.get_or_create(name=d)
    dept_objs.append(obj)
print(f"Created {len(dept_objs)} departments")

# Create leave types
leave_types = [
    ('Annual Leave', 12, True),
    ('Sick Leave', 6, True),
    ('Casual Leave', 3, True),
    ('Maternity Leave', 180, True),
    ('Unpaid Leave', 30, False),
]
for name, days, paid in leave_types:
    LeaveType.objects.get_or_create(name=name, defaults={'max_days_per_year': days, 'is_paid': paid})
print("Leave types created")

# Create sample employees
sample_employees = [
    ('EMP001', 'Rahul', 'Sharma', 'rahul@hrms.com', 'full_time', 'Engineering', 'Senior Developer', 85000),
    ('EMP002', 'Priya', 'Patel', 'priya@hrms.com', 'full_time', 'Human Resources', 'HR Manager', 75000),
    ('EMP003', 'Amit', 'Kumar', 'amit@hrms.com', 'contract', 'Engineering', 'Backend Developer', 60000),
    ('EMP004', 'Sneha', 'Singh', 'sneha@hrms.com', 'part_time', 'Sales & Marketing', 'Marketing Executive', 35000),
    ('EMP005', 'Vikram', 'Verma', 'vikram@hrms.com', 'full_time', 'Finance', 'Finance Analyst', 70000),
    ('EMP006', 'Anjali', 'Gupta', 'anjali@hrms.com', 'part_time', 'Operations', 'Operations Coordinator', 32000),
    ('EMP007', 'Rajesh', 'Mehta', 'rajesh@hrms.com', 'contract', 'Engineering', 'DevOps Engineer', 65000),
]

dept_map = {d.name: d for d in Department.objects.all()}
for emp_id, fn, ln, email, emp_type, dept_name, designation, salary in sample_employees:
    emp, created = Employee.objects.get_or_create(
        employee_id=emp_id,
        defaults={
            'first_name': fn, 'last_name': ln, 'email': email,
            'employee_type': emp_type, 'department': dept_map.get(dept_name),
            'designation': designation, 'basic_salary': salary,
            'date_of_joining': date(2023, 1, 15), 'status': 'active',
        }
    )
    if created:
        print(f"  Created employee: {emp}")

# Create holidays for 2026
holidays_2026 = [
    ('Republic Day', date(2026, 1, 26), 'national'),
    ('Holi', date(2026, 3, 12), 'national'),
    ('Good Friday', date(2026, 4, 3), 'national'),
    ('Eid ul-Fitr', date(2026, 4, 20), 'national'),
    ('Independence Day', date(2026, 8, 15), 'national'),
    ('Gandhi Jayanti', date(2026, 10, 2), 'national'),
    ('Diwali', date(2026, 10, 21), 'national'),
    ('Christmas Day', date(2026, 12, 25), 'national'),
    ('Company Foundation Day', date(2026, 6, 1), 'company'),
    ('Dussehra', date(2026, 10, 9), 'regional'),
]
for name, hdate, htype in holidays_2026:
    Holiday.objects.get_or_create(date=hdate, defaults={'name': name, 'holiday_type': htype})
print(f"Created {len(holidays_2026)} holidays for 2026")

# Generate attendance for previous month (February 2026)
from datetime import timedelta, time
import random
from attendance.models import Attendance
from leaves.models import LeaveRequest

print("Generating attendance and leave data for February 2026...")
start_date = date(2026, 2, 1)
end_date = date(2026, 2, 28)

employees = Employee.objects.all()
leave_type = LeaveType.objects.filter(is_paid=True).first()

attendance_list = []
for emp in employees:
    current_date = start_date
    while current_date <= end_date:
        # Skip weekends (Saturday=5, Sunday=6)
        if current_date.weekday() < 5:
            status = 'present'
            rand_val = random.random()
            
            # 5% chance of absent, 5% chance of leave
            if rand_val < 0.05:
                status = 'absent'
            elif rand_val < 0.10 and leave_type:
                status = 'leave'
                
            check_in_time = time(9, random.randint(0, 30)) if status == 'present' else None
            check_out_time = time(17, random.randint(0, 30)) if status == 'present' else None
            
            if status == 'leave':
                LeaveRequest.objects.get_or_create(
                    employee=emp,
                    start_date=current_date,
                    end_date=current_date,
                    leave_type=leave_type,
                    defaults={'status': 'approved', 'reason': 'Auto-generated leave for testing'}
                )
                
            attendance_list.append(Attendance(
                employee=emp,
                date=current_date,
                status=status,
                check_in=check_in_time,
                check_out=check_out_time,
                notes='Auto-seeded'
            ))
            
        current_date += timedelta(days=1)

# Delete existing attendance for Feb 2026 to avoid duplicate errors on re-run
Attendance.objects.filter(date__range=(start_date, end_date)).delete()
LeaveRequest.objects.filter(start_date__range=(start_date, end_date)).delete()
Attendance.objects.bulk_create(attendance_list, ignore_conflicts=True)
print(f"Created {len(attendance_list)} attendance records for {len(employees)} employees.")

print("\n[SUCCESS] Seed data complete!")
print("Login URL: http://127.0.0.1:8000/login/")
print("Username: admin | Password: admin123")
