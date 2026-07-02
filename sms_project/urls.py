from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg
from datetime import date
from students.models import Student
from teachers.models import Teacher
from courses.models import Course
from subjects.models import Subject
from attendance.models import Attendance
from fees.models import FeePayment
from exams.models import Marks


@login_required
def dashboard_view(request):
    user = request.user
    context = {}

    if user.role == 'admin':
        total_students = Student.objects.count()
        total_teachers = Teacher.objects.count()
        total_courses = Course.objects.count()
        total_subjects = Subject.objects.count()
        today_attendance = Attendance.objects.filter(date=date.today()).count()
        pending_fees = FeePayment.objects.filter(status='pending').count()

        students_by_month = Student.objects.extra(
            select={'month': "strftime('%%m', admission_date)", 'year': "strftime('%%Y', admission_date)"}
        ).values('month', 'year').annotate(count=Count('id')).order_by('year', 'month')

        attendance_stats = Attendance.objects.values('status').annotate(count=Count('id'))
        dept_distribution = Student.objects.values('department__name').annotate(count=Count('id'))

        context.update({
            'total_students': total_students, 'total_teachers': total_teachers,
            'total_courses': total_courses, 'total_subjects': total_subjects,
            'today_attendance': today_attendance, 'pending_fees': pending_fees,
            'students_by_month': list(students_by_month),
            'attendance_stats': list(attendance_stats),
            'dept_distribution': list(dept_distribution),
        })

    elif user.role == 'teacher':
        teacher = Teacher.objects.filter(user=user).first()
        if teacher:
            classes = Subject.objects.filter(teacher=teacher).values('course__name', 'name').distinct()
            context['my_classes'] = classes
            context['pending_attendance'] = Attendance.objects.filter(date=date.today()).count()

    elif user.role == 'student':
        student = Student.objects.filter(user=user).first()
        if student:
            total_attendance = Attendance.objects.filter(student=student).count()
            present = Attendance.objects.filter(student=student, status='present').count()
            context['attendance_pct'] = round(present / total_attendance * 100, 1) if total_attendance else 0
            marks_qs = Marks.objects.filter(student=student)
            total_marks = marks_qs.aggregate(avg=Avg('total_marks'))
            context['avg_marks'] = round(total_marks['avg'], 1) if total_marks['avg'] else 0

    return render(request, 'dashboard.html', context)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard_view, name='dashboard'),
    path('accounts/', include('accounts.urls')),
    path('students/', include('students.urls')),
    path('teachers/', include('teachers.urls')),
    path('departments/', include('departments.urls')),
    path('courses/', include('courses.urls')),
    path('subjects/', include('subjects.urls')),
    path('attendance/', include('attendance.urls')),
    path('exams/', include('exams.urls')),
    path('timetable/', include('timetable.urls')),
    path('assignments/', include('assignments.urls')),
    path('notices/', include('notices.urls')),
    path('fees/', include('fees.urls')),
    path('reports/', include('reports_app.urls')),
    path('api/', include('api.urls')),
]

if settings.DEBUG:
    urlpatterns += [path('__debug__/', include('debug_toolbar.urls'))]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
