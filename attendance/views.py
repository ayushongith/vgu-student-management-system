from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Attendance
from students.models import Student
from subjects.models import Subject
from teachers.models import Teacher
from accounts.decorators import teacher_or_admin_required
from datetime import date


@login_required
def attendance_list(request):
    user = request.user
    if user.role == 'admin':
        records = Attendance.objects.select_related('student__user', 'subject').all()
    elif user.role == 'teacher':
        teacher = Teacher.objects.filter(user=user).first()
        records = Attendance.objects.filter(subject__teacher=teacher).select_related('student__user', 'subject') if teacher else Attendance.objects.none()
    else:
        records = Attendance.objects.none()
    return render(request, 'attendance/attendance_list.html', {'records': records})


@teacher_or_admin_required
def mark_attendance(request):
    if request.user.role == 'admin':
        subjects = Subject.objects.all()
        teacher = None
    else:
        teacher = Teacher.objects.filter(user=request.user).first()
        subjects = teacher.subjects.all() if teacher else Subject.objects.none()

    if request.method == 'POST':
        subject_id = request.POST.get('subject')
        attendance_date = request.POST.get('date')
        student_ids = request.POST.getlist('students')
        statuses = request.POST.getlist('status')

        subject = get_object_or_404(subjects, id=subject_id)

        for student_id, status in zip(student_ids, statuses):
            student = get_object_or_404(Student, id=student_id, course=subject.course)
            Attendance.objects.update_or_create(
                student=student, subject=subject, date=attendance_date,
                defaults={'status': status, 'marked_by': teacher}
            )
        messages.success(request, 'Attendance marked successfully.')
        return redirect('attendance_list')

    subject_id = request.GET.get('subject')
    attendance_date = request.GET.get('date', date.today().isoformat())
    students = Student.objects.none()

    if subject_id:
        subject = get_object_or_404(subjects, id=subject_id)
        students = Student.objects.filter(course=subject.course, semester=subject.course.semester)

    return render(request, 'attendance/mark_attendance.html', {
        'subjects': subjects, 'students': students,
        'selected_subject': subject_id, 'selected_date': attendance_date,
    })
