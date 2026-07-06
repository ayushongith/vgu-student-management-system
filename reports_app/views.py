from django.shortcuts import render, get_object_or_404
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


@login_required
def academic_predictor(request, student_id=None):
    user = request.user
    students_list = None
    selected_student = None

    if user.role in ['admin', 'teacher']:
        students_list = Student.objects.all().select_related('user', 'course')
        if student_id:
            selected_student = get_object_or_404(Student, pk=student_id)
        elif request.GET.get('student'):
            selected_student = get_object_or_404(Student, pk=request.GET.get('student'))
        else:
            selected_student = students_list.first()
    elif user.role == 'student':
        selected_student = get_object_or_404(Student, user=user)
        if student_id and student_id != selected_student.pk:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("You do not have permission to view other students' predictions.")

    if not selected_student:
        return render(request, 'reports_app/student_predictor.html', {
            'error_message': 'No student records found to perform analytics.'
        })

    # Attendance Projections
    attendance_qs = Attendance.objects.filter(student=selected_student)
    total_held = attendance_qs.count()
    present_count = attendance_qs.filter(status='present').count()
    current_pct = round((present_count / total_held * 100), 1) if total_held > 0 else 100.0

    total_semester_classes = 80
    remaining = max(0, total_semester_classes - total_held)
    max_possible_pct = round(((present_count + remaining) / total_semester_classes * 100), 1)
    min_classes_needed_for_75 = max(0, int(0.75 * total_semester_classes) - present_count)

    if current_pct >= 75:
        risk_level = 'safe'
        risk_text = 'Safe'
        risk_class = 'success'
    elif max_possible_pct >= 75:
        risk_level = 'warning'
        risk_text = 'At Risk'
        risk_class = 'warning'
    else:
        risk_level = 'danger'
        risk_text = 'Critical'
        risk_class = 'danger'

    # Academic & CGPA calculations
    marks_qs = Marks.objects.filter(student=selected_student).select_related('exam__subject')
    avg_pct = 0.0
    projected_cgpa = 0.0
    theory_pct = 0.0
    practical_pct = 0.0
    recommendation = "No exam marks available yet. Predictions will update once scores are recorded."

    if marks_qs.exists():
        avg_pct = sum(m.percentage for m in marks_qs) / marks_qs.count()
        projected_cgpa = min(10.0, round((avg_pct / 10.0), 2))

        theory_pct_sum = sum(m.theory_marks for m in marks_qs)
        theory_max_sum = sum(m.exam.max_theory_marks for m in marks_qs)
        practical_pct_sum = sum(m.practical_marks for m in marks_qs)
        practical_max_sum = sum(m.exam.max_practical_marks for m in marks_qs)

        theory_pct = round((theory_pct_sum / theory_max_sum * 100), 1) if theory_max_sum > 0 else 0.0
        practical_pct = round((practical_pct_sum / practical_max_sum * 100), 1) if practical_max_sum > 0 else 0.0

        if theory_pct < 60 and theory_pct < practical_pct:
            recommendation = "Your theory exam scores are significantly trailing your practical results. Focus on textbook readings, theory lectures, and structured notes. Try writing previous years' test papers to practice formatting answers."
        elif practical_pct < 60 and practical_pct < theory_pct:
            recommendation = "Your lab/practical submissions are holding back your academic performance. Ensure you attend all practical sessions, practice lab exercises, and ask for faculty help with lab assignments."
        elif avg_pct < 60:
            recommendation = "Your overall performance requires general improvement. Establish a dedicated study timetable, attend tutoring sessions, and regularly review course syllabus items."
        else:
            recommendation = "Excellent work! Your academic progress is balanced. Continue maintaining your current effort across both lecture rooms and lab sessions."

    return render(request, 'reports_app/student_predictor.html', {
        'students_list': students_list,
        'selected_student': selected_student,
        'attendance': {
            'total_held': total_held,
            'present': present_count,
            'current_pct': current_pct,
            'max_possible': max_possible_pct,
            'min_needed': min_classes_needed_for_75,
            'risk_level': risk_level,
            'risk_text': risk_text,
            'risk_class': risk_class,
        },
        'academics': {
            'avg_pct': round(avg_pct, 1),
            'projected_cgpa': projected_cgpa,
            'theory_pct': theory_pct,
            'practical_pct': practical_pct,
            'recommendation': recommendation,
        }
    })

