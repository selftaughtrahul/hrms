"""
leaves/views.py
Class-Based Views for Leave management.
Business logic delegated to LeaveService.
"""
from django.views.generic import ListView, DetailView, CreateView, UpdateView, View
from django.views import View as BaseView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect

from core.mixins import HRMSLoginMixin, HRMSCreateMixin
from core.exceptions import (
    LeaveConflictError,
    InvalidLeaveStatusTransitionError,
)
from .models import LeaveRequest, LeaveType
from .forms import LeaveRequestForm, LeaveReviewForm, LeaveTypeForm
from .services import LeaveService


class LeaveListView(HRMSLoginMixin, ListView):
    """Display all leave requests with status filter."""
    template_name = 'leaves/list.html'
    context_object_name = 'leaves'

    def get_queryset(self):
        return LeaveService.get_list(
            status_filter=self.request.GET.get('status', '')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        counts = LeaveRequest.objects.get_status_counts()
        context.update({
            'pending_count': counts.get('pending', 0),
            'approved_count': counts.get('approved', 0),
            'rejected_count': counts.get('rejected', 0),
        })
        return context


class LeaveApplyView(HRMSLoginMixin, CreateView):
    """Submit a new leave request."""
    template_name = 'leaves/form.html'
    form_class = LeaveRequestForm
    success_url = reverse_lazy('leave_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Apply for Leave'
        return context

    def form_valid(self, form):
        try:
            LeaveService.apply_leave(form.cleaned_data)
            messages.success(self.request, 'Leave request submitted successfully!')
            return redirect(self.success_url)
        except LeaveConflictError as exc:
            form.add_error(None, str(exc))
            return self.form_invalid(form)


class LeaveDetailView(HRMSLoginMixin, DetailView):
    """Detailed view of a single leave request with review form."""
    template_name = 'leaves/detail.html'
    context_object_name = 'leave'

    def get_queryset(self):
        return LeaveRequest.objects.with_relations()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['review_form'] = LeaveReviewForm()
        return context


class LeaveReviewView(HRMSLoginMixin, BaseView):
    """
    POST-only view to approve or reject a pending leave request.
    Delegates state transition to LeaveService.
    """
    http_method_names = ['post']

    def post(self, request, pk):
        action = request.POST.get('status')
        note = request.POST.get('review_note', '')
        reviewer = request.user.get_full_name() or request.user.username

        try:
            if action == 'approved':
                LeaveService.approve_leave(pk, reviewer, note)
                messages.success(request, 'Leave request approved.')
            elif action == 'rejected':
                LeaveService.reject_leave(pk, reviewer, note)
                messages.warning(request, 'Leave request rejected.')
            else:
                messages.error(request, 'Invalid action.')
        except InvalidLeaveStatusTransitionError as exc:
            messages.error(request, str(exc))

        return redirect('leave_detail', pk=pk)


class LeaveCancelView(HRMSLoginMixin, BaseView):
    """POST-only view to cancel a leave request."""
    template_name = 'leaves/confirm_cancel.html'

    def get(self, request, pk):
        leave = get_object_or_404(LeaveRequest, pk=pk)
        from django.shortcuts import render
        return render(request, self.template_name, {'leave': leave})

    def post(self, request, pk):
        try:
            LeaveService.cancel_leave(pk)
            messages.success(request, 'Leave request cancelled.')
        except InvalidLeaveStatusTransitionError as exc:
            messages.error(request, str(exc))
        return redirect('leave_list')


class LeaveTypeListView(HRMSLoginMixin, ListView):
    """List all configurable leave types."""
    template_name = 'leaves/leave_types.html'
    context_object_name = 'leave_types'
    def get_queryset(self):
        return LeaveType.objects.all()


class LeaveTypeCreateView(HRMSLoginMixin, HRMSCreateMixin, CreateView):
    """Create a leave type."""
    template_name = 'leaves/leave_type_form.html'
    form_class = LeaveTypeForm
    success_url = reverse_lazy('leave_type_list')
    success_message = 'Leave type created!'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Leave Type'
        return context


class LeaveTypeUpdateView(HRMSLoginMixin, HRMSCreateMixin, UpdateView):
    """Update a leave type."""
    template_name = 'leaves/leave_type_form.html'
    form_class = LeaveTypeForm
    model = LeaveType
    success_url = reverse_lazy('leave_type_list')
    success_message = 'Leave type updated!'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Leave Type'
        return context
