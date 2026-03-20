from django.urls import path
from .views_dashboard import DashboardView

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
]
