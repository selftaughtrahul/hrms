"""
core/views_signup.py — Public company signup view for the HRMS SaaS platform.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.db import transaction
from django.views import View

from core.forms import TenantSignupForm
from core.models import Tenant, UserProfile, CompanyConfig


class TenantSignupView(View):
    """
    Allows a new company to sign up for the HRMS SaaS.
    On POST success, atomically creates:
      - Tenant (the company)
      - Django User (the owner/admin)
      - UserProfile (links user to tenant with 'owner' role)
      - CompanyConfig (default settings for the tenant)
    Then logs the user in and redirects to the dashboard.
    """
    template_name = 'auth/signup.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        form = TenantSignupForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = TenantSignupForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                with transaction.atomic():
                    # 1. Create the Tenant
                    tenant = Tenant.objects.create(
                        name=data['company_name'],
                        owner_email=data['email'],
                    )

                    # 2. Create the Django User
                    names = data['admin_name'].strip().split(' ', 1)
                    first_name = names[0]
                    last_name = names[1] if len(names) > 1 else ''
                    username = data['email'].split('@')[0]
                    # Ensure username uniqueness
                    base_username = username
                    counter = 1
                    while User.objects.filter(username=username).exists():
                        username = f"{base_username}{counter}"
                        counter += 1

                    user = User.objects.create_user(
                        username=username,
                        email=data['email'],
                        password=data['password'],
                        first_name=first_name,
                        last_name=last_name,
                    )

                    # 3. Link user to tenant via UserProfile
                    UserProfile.objects.create(
                        user=user,
                        tenant=tenant,
                        role='owner',
                    )

                    # 4. Create default CompanyConfig for this tenant
                    CompanyConfig.objects.create(
                        tenant=tenant,
                        company_name=data['company_name'],
                    )

                # Log the user in and redirect to dashboard
                login(request, user)
                return redirect('dashboard')

            except Exception as e:
                form.add_error(None, f'Sign up failed: {str(e)}. Please try again.')

        return render(request, self.template_name, {'form': form})
