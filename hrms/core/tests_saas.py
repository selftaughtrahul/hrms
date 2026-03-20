from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from core.models import Tenant, UserProfile, CompanyConfig, ActivityLog
from employees.models import Employee, Department
from leaves.models import LeaveRequest, LeaveType
from payroll.models import Payroll
from core.signals import set_current_tenant
import datetime

class SaaSTestCase(TestCase):
    """
    High-standard test suite for HRMS Multi-tenant SaaS architecture.
    Covers data isolation, tenant resolution, and onboarding integrity.
    """

    def setUp(self):
        # 1. Create Tenant A
        self.tenant_a = Tenant.objects.create(name="Company A", slug="comp-a", owner_email="admin@a.com")
        self.user_a = User.objects.create_user(username="admin_a", email="admin@a.com", password="password123", is_staff=True)
        self.profile_a = UserProfile.objects.create(user=self.user_a, tenant=self.tenant_a, role="admin")
        
        # 2. Create Tenant B
        self.tenant_b = Tenant.objects.create(name="Company B", slug="comp-b", owner_email="admin@b.com")
        self.user_b = User.objects.create_user(username="admin_b", email="admin@b.com", password="password123", is_staff=True)
        self.profile_b = UserProfile.objects.create(user=self.user_b, tenant=self.tenant_b, role="admin")

        # 3. Create sample data for Tenant A
        # We bypass the manager by setting the thread-local manually for setup
        set_current_tenant(self.tenant_a)
        self.dept_a = Department.objects.create(tenant=self.tenant_a, name="HR Dept A")
        self.emp_a = Employee.objects.create(
            tenant=self.tenant_a,
            employee_id="EMP-A-001",
            first_name="John",
            last_name="A",
            email="john@a.com",
            department=self.dept_a,
            date_of_joining=datetime.date.today(),
            status='active'
        )
        
        # 4. Create sample data for Tenant B
        set_current_tenant(self.tenant_b)
        self.dept_b = Department.objects.create(tenant=self.tenant_b, name="Dev Dept B")
        self.emp_b = Employee.objects.create(
            tenant=self.tenant_b,
            employee_id="EMP-B-999",
            first_name="Sarah",
            last_name="B",
            email="sarah@b.com",
            department=self.dept_b,
            date_of_joining=datetime.date.today(),
            status='active'
        )
        
        # 5. Create Attendance for both
        from attendance.models import Attendance
        set_current_tenant(self.tenant_a)
        Attendance.objects.create(tenant=self.tenant_a, employee=self.emp_a, date=datetime.date.today(), status='present')
        
        set_current_tenant(self.tenant_b)
        Attendance.objects.create(tenant=self.tenant_b, employee=self.emp_b, date=datetime.date.today(), status='present')

        # Reset current tenant to None (System/Superuser state)
        set_current_tenant(None)

    def test_data_isolation_employees(self):
        """Verify that Company A cannot see Company B's employees."""
        # Log in as Company A Admin
        self.client.login(username="admin_a", password="password123")
        
        # The TenantMiddleware will set tenant_a in thread-local via the profile
        # Employee.objects.all() should only return 1 record (John A)
        response = self.client.get(reverse('employee_list'))
        
        # Check that John A is present and Sarah B is absent
        self.assertContains(response, "John A")
        self.assertNotContains(response, "Sarah B")
        
        # In the test thread, we must manually set tenant to check counts correctly
        set_current_tenant(self.tenant_a)
        self.assertEqual(Employee.objects.count(), 1)
        self.assertEqual(Employee.objects.first().tenant, self.tenant_a)
        set_current_tenant(None)

    def test_data_isolation_departments(self):
        """Verify that Company B cannot see Company A's departments."""
        self.client.login(username="admin_b", password="password123")
        
        response = self.client.get(reverse('department_list'))
        
        self.assertContains(response, "Dev Dept B")
        self.assertNotContains(response, "HR Dept A")
        set_current_tenant(self.tenant_b)
        self.assertEqual(Department.objects.count(), 1)
        set_current_tenant(None)

    def test_cross_tenant_access_denied(self):
        """Verify that directly accessing a foreign tenant's employee URL returns 404."""
        self.client.login(username="admin_b", password="password123")
        
        # Attempt to view Company A's employee John (id=emp_a.pk)
        url = reverse('employee_detail', kwargs={'pk': self.emp_a.pk})
        response = self.client.get(url)
        
        # Should be 404 because Employee.objects.get(pk=...) filters by tenant
        self.assertEqual(response.status_code, 404)

    def test_signup_flow_integrity(self):
        """Verify that the signup flow creates all required SaaS objects."""
        # Public signup doesn't require login
        signup_data = {
            'company_name': 'New Startup Inc',
            'admin_name': 'Alice Founder',
            'email': 'alice@startup.com',
            'password': 'ComplexPassword123!',
            'confirm_password': 'ComplexPassword123!'
        }
        
        response = self.client.post(reverse('signup'), data=signup_data)
        
        # Verify redirect to dashboard
        self.assertEqual(response.status_code, 302)
        
        # Verify objects created
        tenant = Tenant.objects.get(name='New Startup Inc')
        self.assertEqual(tenant.owner_email, 'alice@startup.com')
        
        user = User.objects.get(email='alice@startup.com')
        self.assertEqual(user.first_name, 'Alice')
        
        profile = UserProfile.objects.get(user=user)
        self.assertEqual(profile.tenant, tenant)
        self.assertEqual(profile.role, 'owner')
        
        config = CompanyConfig.objects.get(tenant=tenant)
        self.assertEqual(config.company_name, 'New Startup Inc')

    def test_superuser_all_access(self):
        """Verify that superusers bypass tenant filtering and see everything."""
        superuser = User.objects.create_superuser(username="root", email="root@hrms.com", password="rootpassword")
        self.client.login(username="root", password="rootpassword")
        
        # Employee.objects.all() for a superuser (tenant=None) returns all records
        self.assertEqual(Employee.unscoped.count(), 2) 
        # Note: Even Employee.objects.all() for superuser returns all records 
        # because get_current_tenant() returns None for superusers in the middleware.
        self.assertEqual(Employee.objects.count(), 2)

    def test_activity_log_isolation(self):
        """Verify that activity logs are correctly scoped and isolated."""
        set_current_tenant(self.tenant_a)
        ActivityLog.objects.create(tenant=self.tenant_a, user=self.user_a, action="System", description="Log A")
        
        set_current_tenant(self.tenant_b)
        ActivityLog.objects.create(tenant=self.tenant_b, user=self.user_b, action="System", description="Log B")
        
        set_current_tenant(None)
        
        # Test the Activity API for Tenant A
        logged_in = self.client.login(username="admin_a", password="password123")
        self.assertTrue(logged_in, "Login failed for admin_a")
        response = self.client.get(reverse('api_activities_list'))
        data = response.json()
        
        # 2 logs expected: 1 from signal (Employee created) + 1 explicit Log A
        self.assertEqual(data['unread_count'], 2, f"Expected 2 logs for Tenant A, got {data['unread_count']}. Data: {data}")
        self.assertEqual(data['activities'][0]['description'], 'Log A')
        
        # Test the Activity API for Tenant B
        logged_in = self.client.login(username="admin_b", password="password123")
        self.assertTrue(logged_in, "Login failed for admin_b")
        response = self.client.get(reverse('api_activities_list'))
        data = response.json()
        
        # 2 logs expected: 1 from signal (Employee created) + 1 explicit Log B
        self.assertEqual(data['unread_count'], 2, f"Expected 2 logs for Tenant B, got {data['unread_count']}. Data: {data}")
        self.assertEqual(data['activities'][0]['description'], 'Log B')

    def test_automatic_tenant_assignment(self):
        """Verify that record creation without explicit tenant auto-assigns the current tenant."""
        # Set tenant A in thread
        set_current_tenant(self.tenant_a)
        
        # Create department WITHOUT tenant=self.tenant_a
        new_dept = Department.objects.create(name="Auto Assigned Dept")
        
        # Verify it was assigned correctly
        self.assertEqual(new_dept.tenant, self.tenant_a)
        
        # Test Employee similarly
        new_emp = Employee.objects.create(
            employee_id="AUTO-001",
            first_name="Auto",
            last_name="User",
            email="auto@a.com",
            date_of_joining=datetime.date.today(),
            status='active'
        )
        self.assertEqual(new_emp.tenant, self.tenant_a)
        
        set_current_tenant(None)

    def test_data_isolation_attendance_admin(self):
        """Verify that Company A Admin cannot see Company B's attendance records."""
        self.client.login(username="admin_a", password="password123")
        response = self.client.get(reverse('attendance_manage_list'))
        
        # Should see John A but NOT Sarah B
        self.assertContains(response, "John A")
        self.assertNotContains(response, "Sarah B")

    def test_data_isolation_payroll_admin(self):
        """Verify that Company B Admin cannot see Company A's payroll slips."""
        from payroll.models import Payroll
        set_current_tenant(self.tenant_a)
        Payroll.objects.create(tenant=self.tenant_a, employee=self.emp_a, month=1, year=2026, basic_salary=5000, net_salary=4500)
        
        self.client.login(username="admin_b", password="password123")
        response = self.client.get(reverse('payroll_list'))
        
        # Company B admin looking at payroll list (for month 1, 2026) should NOT see John A's slip
        self.assertNotContains(response, "John A")
        
        set_current_tenant(None)

    def test_employee_form_uniqueness(self):
        """Verify that EmployeeForm uniquely validates fields within a tenant."""
        from employees.forms import EmployeeForm
        
        # 1. Try to create duplicate in Tenant A
        set_current_tenant(self.tenant_a)
        form_data = {
            'employee_id': 'EMP-A-001', # Already exists in Tenant A
            'first_name': 'Duplicate',
            'last_name': 'User',
            'email': 'duplicate@a.com',
            'date_of_joining': datetime.date.today(),
            'status': 'active',
            'gender': 'male',
            'employee_type': 'full_time',
            'basic_salary': 50000,
            'hourly_rate': 0,
            'annual_leave_quota': 12,
            'sick_leave_quota': 6
        }
        form = EmployeeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('employee_id', form.errors)
        self.assertEqual(form.errors['employee_id'][0], "An employee with this ID already exists in your company.")
        
        # 2. Try to use Tenant A's ID in Tenant B (Should be VALID)
        set_current_tenant(self.tenant_b)
        form_data['employee_id'] = 'EMP-A-001' # Exists in A, but NOT in B
        form_data['email'] = 'new@b.com'
        form = EmployeeForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        
        set_current_tenant(None)

    def test_employee_deletion_safeguard(self):
        """Verify that an employee with records (attendance) cannot be deleted."""
        # 1. Login as Admin A
        self.client.login(username="admin_a", password="password123")
        
        # 2. Try to delete emp_a who HAS an attendance record (created in setUp)
        url = reverse('employee_delete', kwargs={'pk': self.emp_a.pk})
        
        # The confirmation page should show counts > 0 and include the warning
        response = self.client.get(url)
        self.assertContains(response, "Action Prohibited")
        self.assertContains(response, "Attendance record")
        
        # The POST request should be intercepted and redirected
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302) # Redirects to list
        
        # Verify employee still exists in DB
        set_current_tenant(self.tenant_a)
        self.assertTrue(Employee.objects.filter(pk=self.emp_a.pk).exists())
        set_current_tenant(None)

    def tearDown(self):
        # Ensure thread-local is clean for the next test
        set_current_tenant(None)
