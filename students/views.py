from django.shortcuts import render, redirect, get_object_or_404
from accounts.decorators import admin_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .models import Student
from .forms import StudentForm
from attendance.models import Attendance
from exams.models import Marks
from departments.models import Department
from timetable.models import Timetable
import csv


@admin_required
def student_list(request):
    students = Student.objects.select_related('user', 'department', 'course').all()
    dept = request.GET.get('department')
    semester = request.GET.get('semester')
    if dept:
        students = students.filter(department_id=dept)
    if semester:
        students = students.filter(semester=semester)
    departments = Department.objects.all()
    return render(request, 'students/student_list.html', {
        'students': students, 'departments': departments
    })


@admin_required
def student_create(request):
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student created successfully.')
            return redirect('student_list')
    else:
        form = StudentForm()
    return render(request, 'students/student_form.html', {'form': form, 'title': 'Add Student'})


@admin_required
def student_update(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student updated successfully.')
            return redirect('student_list')
    else:
        initial = {'first_name': student.user.first_name, 'last_name': student.user.last_name, 'email': student.user.email}
        form = StudentForm(instance=student, initial=initial)
    return render(request, 'students/student_form.html', {'form': form, 'title': 'Edit Student'})


@admin_required
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.user.delete()
        student.delete()
        messages.success(request, 'Student deleted successfully.')
        return redirect('student_list')
    return render(request, 'students/student_confirm_delete.html', {'object': student})


@admin_required
def student_detail(request, pk):
    student = get_object_or_404(Student.objects.select_related('user', 'department', 'course'), pk=pk)
    attendance = Attendance.objects.filter(student=student)[:30]
    marks = Marks.objects.filter(student=student).select_related('exam__subject')
    return render(request, 'students/student_detail.html', {
        'student': student, 'attendance': attendance, 'marks': marks
    })


@login_required
def my_attendance(request):
    student = Student.objects.filter(user=request.user).first()
    if not student:
        messages.error(request, 'Student profile not found.')
        return redirect('dashboard')
    attendance = Attendance.objects.filter(student=student).select_related('subject')
    present_count = attendance.filter(status='present').count()
    total_count = attendance.count()
    pct = round(present_count / total_count * 100, 1) if total_count else 0
    return render(request, 'students/my_attendance.html', {
        'attendance': attendance, 'percentage': pct
    })


@login_required
def my_marks(request):
    student = Student.objects.filter(user=request.user).first()
    if not student:
        messages.error(request, 'Student profile not found.')
        return redirect('dashboard')
    marks = Marks.objects.filter(student=student).select_related('exam__subject')
    return render(request, 'students/my_marks.html', {'marks': marks})


@login_required
def my_timetable(request):
    student = Student.objects.filter(user=request.user).first()
    if not student:
        return redirect('dashboard')
    slots = Timetable.objects.filter(
        course=student.course, semester=student.semester
    ).select_related('subject', 'teacher')
    return render(request, 'students/my_timetable.html', {'slots': slots})


@login_required
def my_assignments(request):
    student = Student.objects.filter(user=request.user).first()
    if not student:
        return redirect('dashboard')
    from assignments.models import Assignment, Submission
    assignments = Assignment.objects.filter(subject__course=student.course).select_related('subject', 'teacher')
    submissions = Submission.objects.filter(student=student)
    submitted_ids = submissions.values_list('assignment_id', flat=True)
    return render(request, 'students/my_assignments.html', {
        'assignments': assignments, 'submitted_ids': list(submitted_ids)
    })


@admin_required
def export_students_csv(request):
    students = Student.objects.select_related('user', 'department', 'course').all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="students.csv"'
    writer = csv.writer(response)
    writer.writerow(['Admission No', 'Roll No', 'Name', 'Email', 'Phone', 'Department', 'Course', 'Semester'])
    for s in students:
        writer.writerow([s.admission_number, s.roll_number, s.user.get_full_name(), s.user.email, s.phone, s.department, s.course, s.semester])
    return response
