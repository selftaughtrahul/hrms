from django.test import TestCase
from datetime import date
from core.exceptions import LeaveConflictError, InvalidLeaveStatusTransitionError
from leaves.models import LeaveRequest, LeaveType
from leaves.services import LeaveService
from employees.models import Employee, Department


class LeaveServiceTest(TestCase):

    def setUp(self):
        self.dept = Department.objects.create(name="Engineering")
        self.employee = Employee.objects.create(
            employee_id='EMP999', first_name='John', last_name='Doe',
            email='john@hrms.test', date_of_joining=date(2026, 1, 1),
            employee_type='full_time', status='active'
        )
        self.leave_type = LeaveType.objects.create(
            name="Annual Leave", max_days_per_year=12
        )

        self.valid_data = {
            'employee': self.employee,
            'leave_type': self.leave_type,
            'start_date': date(2026, 3, 1),
            'end_date': date(2026, 3, 5),
            'reason': 'Vacation',
        }

    def test_apply_leave_success(self):
        leave = LeaveService.apply_leave(self.valid_data)
        self.assertEqual(leave.status, 'pending')
        self.assertEqual(leave.employee, self.employee)
        # March 1st to 5th inclusive is 5 days
        self.assertEqual(leave.total_days, 5)

    def test_apply_leave_conflict(self):
        # First leave applied (pending)
        LeaveService.apply_leave(self.valid_data)

        # Overlapping leave
        conflict_data = self.valid_data.copy()
        conflict_data['start_date'] = date(2026, 3, 4)
        conflict_data['end_date'] = date(2026, 3, 10)

        with self.assertRaises(LeaveConflictError):
            LeaveService.apply_leave(conflict_data)

    def test_approve_leave(self):
        leave = LeaveService.apply_leave(self.valid_data)
        approved_leave = LeaveService.approve_leave(leave.pk, 'Reviewer name', 'Approved')
        self.assertEqual(approved_leave.status, 'approved')
        self.assertEqual(approved_leave.reviewed_by, 'Reviewer name')
        self.assertEqual(approved_leave.review_note, 'Approved')

    def test_reject_leave(self):
        leave = LeaveService.apply_leave(self.valid_data)
        rejected = LeaveService.reject_leave(leave.pk, 'Manager', 'Not allowed right now')
        self.assertEqual(rejected.status, 'rejected')

    def test_invalid_status_transition(self):
        # Apply and approve
        leave = LeaveService.apply_leave(self.valid_data)
        LeaveService.approve_leave(leave.pk, 'Manager')
        
        # Cannot reject an already approved leave based on our rules
        with self.assertRaises(InvalidLeaveStatusTransitionError):
            LeaveService.reject_leave(leave.pk, 'Manager')

    def test_cancel_leave(self):
        leave = LeaveService.apply_leave(self.valid_data)
        cancelled = LeaveService.cancel_leave(leave.pk)
        self.assertEqual(cancelled.status, 'cancelled')

        # Cannot cancel an already cancelled leave
        with self.assertRaises(InvalidLeaveStatusTransitionError):
            LeaveService.cancel_leave(cancelled.pk)

    def test_get_leave_balance(self):
        # Setup: 10 days Annual Quota. Employee takes 4 days.
        lt = LeaveType.objects.create(name="Sick", max_days_per_year=10)
        
        # Apply and approve
        data = self.valid_data.copy()
        data['start_date'] = date(2026, 5, 1)
        data['end_date'] = date(2026, 5, 4)  # 4 days total
        data['leave_type'] = lt
        leave = LeaveService.apply_leave(data)
        LeaveService.approve_leave(leave.pk, 'Mgr')

        # Check balance
        balances = LeaveService.get_leave_balance(self.employee)
        
        self.assertIn('Sick', balances)
        self.assertEqual(balances['Sick']['quota'], 10)
        self.assertEqual(balances['Sick']['taken'], 4)
        self.assertEqual(balances['Sick']['remaining'], 6)
