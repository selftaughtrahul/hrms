"""
holidays/urls.py — Updated to use Class-Based View .as_view()
"""
from django.urls import path
from .views import (
    HolidayListView, HolidayCreateView,
    HolidayUpdateView, HolidayDeleteView,
)

urlpatterns = [
    path('', HolidayListView.as_view(), name='holiday_list'),
    path('create/', HolidayCreateView.as_view(), name='holiday_create'),
    path('<int:pk>/edit/', HolidayUpdateView.as_view(), name='holiday_edit'),
    path('<int:pk>/delete/', HolidayDeleteView.as_view(), name='holiday_delete'),
]
