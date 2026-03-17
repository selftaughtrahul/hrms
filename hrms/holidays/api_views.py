from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Holiday
from .serializers import HolidaySerializer
from .services import HolidayService
from datetime import date

class HolidayListCreateAPIView(generics.ListCreateAPIView):
    """
    GET: List all holidays (optionally filter by year).
    POST: Create a new holiday.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = HolidaySerializer

    def get_queryset(self):
        year = self.request.query_params.get('year')
        if year:
            return HolidayService.get_for_year(int(year))
        return Holiday.objects.all().order_by('date')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Using Service layer
        holiday = HolidayService.create_holiday(serializer.validated_data)
        out_serializer = self.get_serializer(holiday)
        return Response(out_serializer.data, status=status.HTTP_201_CREATED)


class HolidayUpcomingAPIView(generics.ListAPIView):
    """GET: List upcoming holidays from today onwards."""
    permission_classes = [IsAuthenticated]
    serializer_class = HolidaySerializer

    def get_queryset(self):
        return HolidayService.get_upcoming(limit=10)
