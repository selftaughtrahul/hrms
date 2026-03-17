"""
leaves/urls.py — Updated to use Class-Based View .as_view()
"""
from django.urls import path
from .views import (
    LeaveListView, LeaveApplyView, LeaveDetailView,
    LeaveReviewView, LeaveCancelView,
    LeaveTypeListView, LeaveTypeCreateView, LeaveTypeUpdateView,
)

urlpatterns = [
    path('', LeaveListView.as_view(), name='leave_list'),
    path('apply/', LeaveApplyView.as_view(), name='leave_apply'),
    path('<int:pk>/', LeaveDetailView.as_view(), name='leave_detail'),
    path('<int:pk>/review/', LeaveReviewView.as_view(), name='leave_review'),
    path('<int:pk>/cancel/', LeaveCancelView.as_view(), name='leave_cancel'),
    path('types/', LeaveTypeListView.as_view(), name='leave_type_list'),
    path('types/create/', LeaveTypeCreateView.as_view(), name='leave_type_create'),
    path('types/<int:pk>/edit/', LeaveTypeUpdateView.as_view(), name='leave_type_edit'),
]
