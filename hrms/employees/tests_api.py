from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from employees.models import Employee, Department
from django.contrib.auth.models import User
from datetime import date

class EmployeeAPITests(APITestCase):

    def setUp(self):
        # Create an auth user
        self.user = User.objects.create_user(username='admin', password='testpassword')
        
        # Create an employee
        self.dept = Department.objects.create(name='IT')
        self.employee = Employee.objects.create(
            employee_id='E001',
            first_name='API',
            last_name='User',
            email='api@test.com',
            department=self.dept,
            date_of_joining=date(2026, 1, 1),
            basic_salary=60000,
            status='active'
        )

    def test_jwt_auth_required(self):
        url = reverse('api_employee_list_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_employees_authenticated(self):
        # Get JWT token
        token_url = reverse('token_obtain_pair')
        token_response = self.client.post(token_url, {'username': 'admin', 'password': 'testpassword'})
        self.assertEqual(token_response.status_code, status.HTTP_200_OK)
        
        token = token_response.data['access']
        
        # Fetch employees
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        url = reverse('api_employee_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['employee_id'], 'E001')
        self.assertEqual(response.data['results'][0]['department_name'], 'IT')
