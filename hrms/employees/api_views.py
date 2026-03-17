from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from core.exceptions import DuplicateEmployeeIDError, EmployeeNotFoundError
from .models import Employee, Department
from .serializers import (
    EmployeeListSerializer, 
    EmployeeDetailSerializer, 
    DepartmentSerializer
)
from .services import EmployeeService, DepartmentService


class EmployeeListCreateAPIView(generics.ListCreateAPIView):
    """
    GET: List all employees (filterable).
    POST: Create a new employee using the Service layer.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return EmployeeService.get_filtered_list(
            query=self.request.query_params.get('q', ''),
            emp_type=self.request.query_params.get('type', ''),
            department_id=self.request.query_params.get('department', ''),
            status=self.request.query_params.get('status', ''),
        )

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return EmployeeDetailSerializer
        return EmployeeListSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            # Delegate entirely to the Service Layer
            employee = EmployeeService.create_employee(serializer.validated_data)
            out_serializer = EmployeeDetailSerializer(employee)
            return Response(out_serializer.data, status=status.HTTP_201_CREATED)
        except DuplicateEmployeeIDError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class EmployeeRetrieveUpdateAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve employee details.
    PUT/PATCH: Update employee using the Service layer.
    DELETE: Soft-delete/deactivate employee using the Service layer.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeDetailSerializer
    queryset = Employee.objects.all() # Used by DRF just for get_object() lookup

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # Delegate to Service Layer
        employee = EmployeeService.update_employee(instance.pk, serializer.validated_data)
        return Response(EmployeeDetailSerializer(employee).data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        EmployeeService.deactivate_employee(instance.pk)
        return Response(status=status.HTTP_204_NO_CONTENT)


class DepartmentListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DepartmentSerializer
    
    def get_queryset(self):
        return DepartmentService.get_all()
