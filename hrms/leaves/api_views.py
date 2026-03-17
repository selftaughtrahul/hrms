from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from core.exceptions import LeaveConflictError, InvalidLeaveStatusTransitionError
from .models import LeaveRequest, LeaveType
from .serializers import LeaveRequestSerializer, LeaveTypeSerializer
from .services import LeaveService


class LeaveTypeListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LeaveTypeSerializer
    queryset = LeaveType.objects.all()


class LeaveRequestListCreateAPIView(generics.ListCreateAPIView):
    """
    GET: List leaves (filtered by status or employee).
    POST: Apply for a new leave using the Service Layer.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = LeaveRequestSerializer

    def get_queryset(self):
        query_status = self.request.query_params.get('status', '')
        employee_id = self.request.query_params.get('employee_id')
        
        qs = LeaveService.get_list(query_status)
        if employee_id:
            qs = qs.filter(employee_id=employee_id)
        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            leave = LeaveService.apply_leave(serializer.validated_data)
            out_serializer = self.get_serializer(leave)
            return Response(out_serializer.data, status=status.HTTP_201_CREATED)
        except LeaveConflictError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LeaveRequestDetailAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LeaveRequestSerializer
    queryset = LeaveRequest.objects.all()


class LeaveReviewAPIView(generics.UpdateAPIView):
    """
    PATCH: Approve or Reject a leave.
    Payload: {"action": "approve" | "reject", "note": "optional string"}
    """
    permission_classes = [IsAuthenticated]
    serializer_class = LeaveRequestSerializer
    queryset = LeaveRequest.objects.all()

    def update(self, request, *args, **kwargs):
        action = request.data.get('action')
        note = request.data.get('note', '')
        instance = self.get_object()
        reviewer_name = request.user.get_full_name() or request.user.username

        try:
            if action == 'approve':
                leave = LeaveService.approve_leave(instance.pk, reviewer_name, note)
            elif action == 'reject':
                leave = LeaveService.reject_leave(instance.pk, reviewer_name, note)
            else:
                return Response({"detail": "Invalid action. Use 'approve' or 'reject'."}, status=status.HTTP_400_BAD_REQUEST)
                
            out_serializer = self.get_serializer(leave)
            return Response(out_serializer.data)
        except InvalidLeaveStatusTransitionError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
