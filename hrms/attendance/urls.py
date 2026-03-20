from django.urls import path
from .views import (
    AttendanceRecordView, PunchInView, PunchOutView,
    AttendanceAdminListView, AttendanceCreateView, AttendanceUpdateView, AttendanceDeleteView
)

urlpatterns = [
    # Employee views
    path('', AttendanceRecordView.as_view(), name='attendance_record'),
    path('punch-in/', PunchInView.as_view(), name='attendance_punch_in'),
    path('punch-out/', PunchOutView.as_view(), name='attendance_punch_out'),

    # Admin views
    path('manage/', AttendanceAdminListView.as_view(), name='attendance_manage_list'),
    path('manage/add/', AttendanceCreateView.as_view(), name='attendance_add'),
    path('manage/<int:pk>/edit/', AttendanceUpdateView.as_view(), name='attendance_edit'),
    path('manage/<int:pk>/delete/', AttendanceDeleteView.as_view(), name='attendance_delete'),
]
