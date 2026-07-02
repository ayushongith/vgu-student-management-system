from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.decorators import admin_required
from django.db.models import Count, Avg, Sum
from students.models import Student
from teachers.models import Teacher
from attendance.models import Attendance
from exams.models import Marks, Exam
from fees.models import FeePayment
from datetime import date, timedelta
import json


@admin_required
def reports_dashboard(request):
    return render(request, 'reports_app/reports_dashboard.html')


@admin_required
def attendance_report(request):
    from django.db.models import Q
    start_date = request.GET.get('from', (date.today() - timedelta(days=30)).isoformat())
    end_date = request.GET.get('to', date.today().isoformat())

    report = Attendance.objects.filter(date__gte=start_date, date__lte=end_date) \
        .values('status').annotate(count=Count('id'))

    daily = Attendance.objects.filter(date__gte=start_date, date__lte=end_date) \
        .values('date', 'status').annotate(count=Count('id')).order_by('date')

    return render(request, 'reports_app/attendance_report.html', {
        'report': report, 'daily': list(daily),
        'start_date': start_date, 'end_date': end_date
    })


@admin_required
def exam_report(request):
    exam_id = request.GET.get('exam')
    exams = Exam.objects.all()
    marks_data = []
    if exam_id:
        marks_qs = Marks.objects.filter(exam_id=exam_id).select_related('student__user')
        for m in marks_qs:
            marks_data.append({
                'student': m.student.user.get_full_name(),
                'roll': m.student.roll_number,
                'theory': m.theory_marks,
                'practical': m.practical_marks,
                'total': m.total_marks,
                'grade': m.grade,
                'pct': m.percentage,
            })
        avg = Marks.objects.filter(exam_id=exam_id).aggregate(
            avg_total=Avg('total_marks'), avg_theory=Avg('theory_marks'), avg_practical=Avg('practical_marks')
        )
    else:
        avg = {}

    return render(request, 'reports_app/exam_report.html', {
        'exams': exams, 'marks_data': marks_data, 'avg': avg, 'selected_exam': exam_id
    })


@admin_required
def fee_report(request):
    total_collected = FeePayment.objects.filter(status='paid').aggregate(total=Sum('amount_paid'))
    pending = FeePayment.objects.filter(status='pending').count()
    paid = FeePayment.objects.filter(status='paid').count()
    return render(request, 'reports_app/fee_report.html', {
        'total_collected': total_collected['total'] or 0,
        'pending': pending, 'paid': paid
    })
