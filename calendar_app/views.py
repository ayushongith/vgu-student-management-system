from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.utils import timezone
from .models import Event
from exams.models import Exam
from assignments.models import Assignment
from notices.models import Notice
from datetime import datetime


@login_required
def calendar_view(request):
    return render(request, 'calendar_app/calendar.html')


@login_required
def get_calendar_events(request):
    events = []

    # 1. Fetch Custom Events
    for e in Event.objects.all():
        color = '#6c757d'
        if e.event_type == 'holiday':
            color = '#dc3545'
        elif e.event_type == 'exam':
            color = '#fd7e14'
        elif e.event_type == 'seminar':
            color = '#0d6efd'
        elif e.event_type == 'cultural':
            color = '#6f42c1'
            
        events.append({
            'id': f'custom_{e.id}',
            'title': e.title,
            'start': e.start_time.isoformat(),
            'end': e.end_time.isoformat(),
            'description': e.description,
            'backgroundColor': color,
            'borderColor': color,
            'textColor': '#ffffff',
            'allDay': False
        })

    # 2. Fetch Exams
    for exam in Exam.objects.select_related('subject').all():
        exam_color = '#fd7e14'
        dt_start = datetime.combine(exam.exam_date, datetime.min.time())
        events.append({
            'id': f'exam_{exam.id}',
            'title': f'Exam: {exam.name} ({exam.subject.code})',
            'start': dt_start.isoformat(),
            'description': f'Subject: {exam.subject.name}. Semester: {exam.semester}',
            'backgroundColor': exam_color,
            'borderColor': exam_color,
            'textColor': '#ffffff',
            'allDay': True
        })

    # 3. Fetch Assignments
    for assignment in Assignment.objects.select_related('subject').all():
        assign_color = '#198754'
        dt_start = datetime.combine(assignment.due_date, datetime.min.time())
        events.append({
            'id': f'assignment_{assignment.id}',
            'title': f'Due: {assignment.title} ({assignment.subject.code})',
            'start': dt_start.isoformat(),
            'description': f'Description: {assignment.description}. Max Marks: {assignment.max_marks}',
            'backgroundColor': assign_color,
            'borderColor': assign_color,
            'textColor': '#ffffff',
            'allDay': True
        })

    # 4. Fetch Active Notices
    for notice in Notice.objects.filter(is_active=True):
        notice_color = '#0dcaf0'
        events.append({
            'id': f'notice_{notice.id}',
            'title': f'Notice: {notice.title}',
            'start': notice.created_at.isoformat(),
            'description': notice.content,
            'backgroundColor': notice_color,
            'borderColor': notice_color,
            'textColor': '#ffffff',
            'allDay': False
        })

    return JsonResponse(events, safe=False)


@login_required
def create_event(request):
    if request.user.role not in ['admin', 'teacher']:
        return HttpResponseForbidden("You do not have permission to schedule calendar events.")

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        start_str = request.POST.get('start_time')
        end_str = request.POST.get('end_time')
        event_type = request.POST.get('event_type', 'other')

        if title and start_str and end_str:
            try:
                start_time = datetime.fromisoformat(start_str)
                end_time = datetime.fromisoformat(end_str)
                if timezone.is_naive(start_time):
                    start_time = timezone.make_aware(start_time)
                if timezone.is_naive(end_time):
                    end_time = timezone.make_aware(end_time)

                Event.objects.create(
                    title=title,
                    description=description,
                    start_time=start_time,
                    end_time=end_time,
                    event_type=event_type,
                    created_by=request.user
                )
                return JsonResponse({'status': 'success'})
            except ValueError as ex:
                return JsonResponse({'status': 'error', 'message': str(ex)}, status=400)

        return JsonResponse({'status': 'error', 'message': 'Missing fields'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
