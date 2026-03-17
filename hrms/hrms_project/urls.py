from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('dashboard'), name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', include('employees.urls_dashboard')),
    path('employees/', include('employees.urls')),
    path('leaves/', include('leaves.urls')),
    path('holidays/', include('holidays.urls')),
    path('payroll/', include('payroll.urls')),
    path('attendance/', include('attendance.urls')),
    
    # Core API (Realtime polling)
    path('api/', include('core.urls')),
    
    # REST API V1 for Mobile Apps
    path('api/v1/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/employees/', include('employees.api_urls')),
    path('api/v1/leaves/', include('leaves.api_urls')),
    path('api/v1/holidays/', include('holidays.api_urls')),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
