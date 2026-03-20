from django.urls import path
from .api_views import (
    LeaveTypeListAPIView,
    LeaveRequestListCreateAPIView,
    LeaveRequestDetailAPIView,
    LeaveReviewAPIView
)

urlpatterns = [
    path('types/', LeaveTypeListAPIView.as_view(), name='api_leave_types'),
    path('', LeaveRequestListCreateAPIView.as_view(), name='api_leave_list_create'),
    path('<int:pk>/', LeaveRequestDetailAPIView.as_view(), name='api_leave_detail'),
    path('<int:pk>/review/', LeaveReviewAPIView.as_view(), name='api_leave_review'),
]
