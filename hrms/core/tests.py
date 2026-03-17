from django.test import TestCase
from datetime import date
from decimal import Decimal
from core.utils import (
    calculate_gross_salary,
    calculate_total_deductions,
    calculate_net_salary,
    get_working_days,
    get_calendar_days,
    get_month_label,
    format_currency
)
from core.exceptions import HRMSBaseException


class MockPayroll:
    """Mock object replacing Payroll for testing utils without DB."""
    def __init__(self, basic, hra, ta, oa, ot, pf, tax, od, ld):
        self.basic_salary = Decimal(str(basic))
        self.hra = Decimal(str(hra))
        self.travel_allowance = Decimal(str(ta))
        self.other_allowances = Decimal(str(oa))
        self.overtime_pay = Decimal(str(ot))
        
        self.pf_deduction = Decimal(str(pf))
        self.tax_deduction = Decimal(str(tax))
        self.other_deductions = Decimal(str(od))
        self.leave_deductions = Decimal(str(ld))


class CoreUtilsTest(TestCase):

    def test_calculate_gross_salary(self):
        payroll = MockPayroll(1000, 400, 100, 50, 20,   0, 0, 0, 0)
        self.assertEqual(calculate_gross_salary(payroll), Decimal('1570'))

    def test_calculate_total_deductions(self):
        payroll = MockPayroll(0, 0, 0, 0, 0,   120, 50, 10, 5)
        self.assertEqual(calculate_total_deductions(payroll), Decimal('185'))

    def test_calculate_net_salary(self):
        payroll = MockPayroll(1000, 400, 100, 0, 0,   120, 50, 0, 0)
        # Gross: 1500, Deductions: 170 -> Net: 1330
        self.assertEqual(calculate_net_salary(payroll), Decimal('1330'))

    def test_calculate_net_salary_floor(self):
        """Net salary should never be negative."""
        payroll = MockPayroll(1000, 0, 0, 0, 0,   2000, 0, 0, 0)
        self.assertEqual(calculate_net_salary(payroll), Decimal('0.00'))

    def test_get_working_days(self):
        # Mon 2nd March to Sun 8th March 2026 (5 working days)
        start = date(2026, 3, 2)
        end = date(2026, 3, 8)
        self.assertEqual(get_working_days(start, end), 5)

        # Start date after end date
        self.assertEqual(get_working_days(end, start), 0)

    def test_get_calendar_days(self):
        start = date(2026, 3, 2)
        end = date(2026, 3, 8)
        self.assertEqual(get_calendar_days(start, end), 7)

    def test_get_month_label(self):
        self.assertEqual(get_month_label(1), 'January')
        self.assertEqual(get_month_label(12), 'December')
        with self.assertRaises(ValueError):
            get_month_label(13)

    def test_format_currency(self):
        self.assertEqual(format_currency(1500.5), '₹1,500.50')
        self.assertEqual(format_currency('abc'), '₹0.00')

        
class HRMSExceptionsTest(TestCase):
    def test_base_exception(self):
        exc = HRMSBaseException("Custom error")
        self.assertEqual(str(exc), "Custom error")
        
    def test_base_exception_default(self):
        exc = HRMSBaseException()
        self.assertEqual(str(exc), "An HRMS error occurred.")
