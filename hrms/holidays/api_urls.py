from django.urls import path
from .api_views import (
    HolidayListCreateAPIView,
    HolidayUpcomingAPIView
)

urlpatterns = [
    path('', HolidayListCreateAPIView.as_view(), name='api_holiday_list_create'),
    path('upcoming/', HolidayUpcomingAPIView.as_view(), name='api_holiday_upcoming'),
]
