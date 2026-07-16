from django.shortcuts import render, redirect, get_object_or_404
from accounts.decorators import admin_required
from django.contrib import messages
from .models import Subject
from .forms import SubjectForm


@admin_required
def subject_list(request):
    subjects = Subject.objects.select_related('course', 'teacher').all()
    return render(request, 'subjects/subject_list.html', {'subjects': subjects})


@admin_required
def subject_create(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject created successfully.')
            return redirect('subject_list')
    else:
        form = SubjectForm()
    return render(request, 'subjects/subject_form.html', {'form': form, 'title': 'Add Subject'})


@admin_required
def subject_update(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject updated successfully.')
            return redirect('subject_list')
    else:
        form = SubjectForm(instance=subject)
    return render(request, 'subjects/subject_form.html', {'form': form, 'title': 'Edit Subject'})


@admin_required
def subject_delete(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        subject.delete()
        messages.success(request, 'Subject deleted successfully.')
        return redirect('subject_list')
    return render(request, 'subjects/subject_confirm_delete.html', {'object': subject})


from django.contrib.auth.decorators import login_required
from students.models import Student
from .models import ElectiveEnrollment
from django.db.models import Count


@login_required
def electives_list(request):
    student = Student.objects.filter(user=request.user).first()
    if not student:
        messages.error(request, 'Student profile not found.')
        return redirect('dashboard')

    # Fetch electives matching student course and active semester
    electives = Subject.objects.filter(
        course=student.course,
        semester=student.semester,
        is_elective=True,
        is_active=True
    ).annotate(enrolled_count=Count('enrollments'))

    # Get IDs of electives this student is enrolled in
    enrolled_ids = set(
        ElectiveEnrollment.objects.filter(student=student)
        .values_list('subject_id', flat=True)
    )

    return render(request, 'subjects/electives_list.html', {
        'electives': electives,
        'enrolled_ids': enrolled_ids,
        'student': student
    })


@login_required
def enroll_elective(request, subject_id):
    if request.method != 'POST':
        return redirect('electives_list')

    student = Student.objects.filter(user=request.user).first()
    if not student:
        messages.error(request, 'Student profile not found.')
        return redirect('dashboard')

    subject = get_object_or_404(
        Subject, pk=subject_id, is_elective=True, is_active=True,
        course=student.course, semester=student.semester
    )

    # Check capacity limit
    enrolled_count = ElectiveEnrollment.objects.filter(subject=subject).count()
    if enrolled_count >= subject.max_capacity:
        messages.error(request, f"Enrollment failed: '{subject.name}' has reached its maximum capacity of {subject.max_capacity} students.")
        return redirect('electives_list')

    # Create enrollment
    ElectiveEnrollment.objects.get_or_create(student=student, subject=subject)
    messages.success(request, f"Successfully enrolled in elective: {subject.name} ({subject.code}).")
    return redirect('electives_list')


@login_required
def withdraw_elective(request, subject_id):
    if request.method != 'POST':
        return redirect('electives_list')

    student = Student.objects.filter(user=request.user).first()
    if not student:
        messages.error(request, 'Student profile not found.')
        return redirect('dashboard')

    subject = get_object_or_404(Subject, pk=subject_id)
    
    # Delete enrollment
    enrollment = ElectiveEnrollment.objects.filter(student=student, subject=subject)
    if enrollment.exists():
        enrollment.delete()
        messages.success(request, f"Successfully withdrawn from elective: {subject.name}.")
    else:
        messages.error(request, "You are not enrolled in this elective.")

    return redirect('electives_list')
