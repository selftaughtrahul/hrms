from django.test import TestCase
from datetime import date
from core.exceptions import PayrollAlreadyExistsError, InvalidPayrollStateError
from payroll.models import Payroll
from payroll.services import PayrollService
from employees.models import Employee


class PayrollServiceTest(TestCase):

    def setUp(self):
        self.employee = Employee.objects.create(
            employee_id='EMP001', first_name='John', last_name='Doe',
            email='john@hrms.test', date_of_joining=date(2026, 1, 1),
            employee_type='full_time', status='active',
            basic_salary=50000
        )
        self.valid_data = {
            'employee': self.employee,
            'month': 3,
            'year': 2026,
            'basic_salary': 50000,
            'hra': 20000,
            'tax_deduction': 5000
        }

    def test_create_payroll_calculates_totals(self):
        payroll = PayrollService.create_payroll(self.valid_data)
        
        # 50k basic + 20k hra = 70k gross
        self.assertEqual(payroll.gross_salary, 70000)
        # 70k gross - 5k tax = 65k net
        self.assertEqual(payroll.net_salary, 65000)
        self.assertEqual(payroll.status, 'draft')

    def test_create_duplicate_payroll(self):
        PayrollService.create_payroll(self.valid_data)
        
        # Creating again for the same employee, month, and year should fail
        with self.assertRaises(PayrollAlreadyExistsError):
            PayrollService.create_payroll(self.valid_data)

    def test_update_payroll_recalculates(self):
        payroll = PayrollService.create_payroll(self.valid_data)
        
        # Increase basic salary
        update_data = self.valid_data.copy()
        update_data['basic_salary'] = 60000
        
        updated = PayrollService.update_payroll(payroll.pk, update_data)
        
        # 60k + 20k hra = 80k gross
        self.assertEqual(updated.gross_salary, 80000)
        # 80k - 5k tax = 75k net
        self.assertEqual(updated.net_salary, 75000)

    def test_cannot_update_paid_payroll(self):
        payroll = PayrollService.create_payroll(self.valid_data)
        PayrollService.mark_as_paid(payroll.pk)
        
        with self.assertRaises(InvalidPayrollStateError):
            PayrollService.update_payroll(payroll.pk, self.valid_data)

    def test_mark_as_paid(self):
        payroll = PayrollService.create_payroll(self.valid_data)
        paid = PayrollService.mark_as_paid(payroll.pk)
        
        self.assertEqual(paid.status, 'paid')
        self.assertEqual(paid.payment_date, date.today())

    def test_get_monthly_summary(self):
        # Create 2 payrolls for same month, one paid
        p1 = PayrollService.create_payroll(self.valid_data)
        PayrollService.mark_as_paid(p1.pk)
        
        emp2 = Employee.objects.create(
            employee_id='EMP002', first_name='Jane', email='jane@test',
            date_of_joining=date.today(), basic_salary=40000
        )
        data2 = self.valid_data.copy()
        data2['employee'] = emp2
        data2['basic_salary'] = 40000
        PayrollService.create_payroll(data2)
        
        summary = PayrollService.get_monthly_summary(3, 2026)
        
        # Total = 2, Paid = 1, Draft = 1
        self.assertEqual(summary['total_records'], 2)
        self.assertEqual(summary['paid_count'], 1)
        self.assertEqual(summary['draft_count'], 1)
        
        # p1 net: 65,000. p2 net: 40k+20k-5k = 55,000. Total = 120,000
        self.assertEqual(summary['total_net'], 120000)
