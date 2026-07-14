from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from .models import AuditLog


@login_required
def audit_logs_list(request):
    if request.user.role != 'admin':
        raise PermissionDenied("You do not have administrative privileges to inspect audit trail logs.")

    logs_qs = AuditLog.objects.select_related('user').all()

    # Search filter
    q = request.GET.get('q', '')
    if q:
        logs_qs = logs_qs.filter(
            user__username__icontains=q
        ) | logs_qs.filter(
            action__icontains=q
        ) | logs_qs.filter(
            details__icontains=q
        )

    # Model filter
    model_filter = request.GET.get('model', '')
    if model_filter:
        logs_qs = logs_qs.filter(model_name=model_filter)

    # Pagination
    paginator = Paginator(logs_qs, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    unique_models = ['Marks', 'FeePayment', 'Notice', 'Timetable', 'Attendance', 'User']

    return render(request, 'audit_logs/logs_list.html', {
        'page_obj': page_obj,
        'q': q,
        'model_filter': model_filter,
        'unique_models': unique_models
    })
