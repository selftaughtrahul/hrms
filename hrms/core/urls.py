from django.urls import path
from .views import ActivityListAPIView, ActivityMarkReadAPIView, CompanyConfigUpdateView

urlpatterns = [
    path('activities/', ActivityListAPIView.as_view(), name='api_activities_list'),
    path('activities/mark-read/', ActivityMarkReadAPIView.as_view(), name='api_activities_mark_read'),
    path('settings/global/', CompanyConfigUpdateView.as_view(), name='core_settings_global'),
]
