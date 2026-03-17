from django.test import TestCase
from datetime import date
from core.exceptions import DuplicateEmployeeIDError, EmployeeNotFoundError
from employees.models import Employee, Department
from employees.services import EmployeeService, DepartmentService


class EmployeeServiceTest(TestCase):

    def setUp(self):
        self.dept = Department.objects.create(name="Engineering")
        self.valid_data = {
            'employee_id': 'EMP999',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@hrms.test',
            'employee_type': 'full_time',
            'department': self.dept,
            'date_of_joining': date(2026, 1, 1),
            'basic_salary': 50000,
            'status': 'active'
        }

    def test_create_employee_success(self):
        emp = EmployeeService.create_employee(self.valid_data)
        self.assertEqual(emp.employee_id, 'EMP999')
        self.assertEqual(Employee.objects.count(), 1)

    def test_create_employee_duplicate_id(self):
        EmployeeService.create_employee(self.valid_data)
        
        # Second employee with same ID should fail
        data2 = self.valid_data.copy()
        data2['email'] = 'jane@hrms.test'
        with self.assertRaises(DuplicateEmployeeIDError):
            EmployeeService.create_employee(data2)

    def test_get_employee_success(self):
        emp1 = EmployeeService.create_employee(self.valid_data)
        emp2 = EmployeeService.get_employee(emp1.pk)
        self.assertEqual(emp1, emp2)

    def test_get_employee_not_found(self):
        with self.assertRaises(EmployeeNotFoundError):
            EmployeeService.get_employee(9999)

    def test_update_employee(self):
        emp = EmployeeService.create_employee(self.valid_data)
        updated = EmployeeService.update_employee(emp.pk, {'first_name': 'Jane'})
        self.assertEqual(updated.first_name, 'Jane')

    def test_deactivate_employee(self):
        emp = EmployeeService.create_employee(self.valid_data)
        EmployeeService.deactivate_employee(emp.pk)
        emp.refresh_from_db()
        self.assertEqual(emp.status, 'inactive')

    def test_get_dashboard_stats(self):
        EmployeeService.create_employee(self.valid_data)
        
        data2 = self.valid_data.copy()
        data2['employee_id'] = 'EMP888'
        data2['email'] = 'pt@hrms.test'
        data2['employee_type'] = 'part_time'
        EmployeeService.create_employee(data2)
        
        stats = EmployeeService.get_dashboard_stats()
        self.assertEqual(stats['total'], 2)
        self.assertEqual(stats['full_time'], 1)
        self.assertEqual(stats['part_time'], 1)

    def test_get_filtered_list(self):
        EmployeeService.create_employee(self.valid_data)
        
        qs = EmployeeService.get_filtered_list(query='John')
        self.assertEqual(qs.count(), 1)
        
        qs = EmployeeService.get_filtered_list(emp_type='contract')
        self.assertEqual(qs.count(), 0)

        
class DepartmentServiceTest(TestCase):
    def test_create_dept(self):
        dept = DepartmentService.create_department({'name': 'HR'})
        self.assertEqual(dept.name, 'HR')
        
    def test_update_dept(self):
        dept = DepartmentService.create_department({'name': 'HR'})
        updated = DepartmentService.update_department(dept.pk, {'name': 'Human Resources'})
        self.assertEqual(updated.name, 'Human Resources')
