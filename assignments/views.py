from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Assignment, Submission
from .forms import AssignmentForm
from students.models import Student
from teachers.models import Teacher
from accounts.decorators import teacher_or_admin_required


def _teacher_for_user(user):
    return Teacher.objects.filter(user=user).first()


def _assignment_form(*args, user, **kwargs):
    form = AssignmentForm(*args, **kwargs)
    if user.role == 'teacher':
        teacher = _teacher_for_user(user)
        if teacher:
            form.fields['teacher'].queryset = Teacher.objects.filter(pk=teacher.pk)
            form.fields['teacher'].initial = teacher
            form.fields['teacher'].disabled = True
            form.fields['subject'].queryset = teacher.subjects.all()
    return form


@login_required
def assignment_list(request):
    assignments = Assignment.objects.select_related('subject', 'teacher').all()
    return render(request, 'assignments/assignment_list.html', {'assignments': assignments})


@teacher_or_admin_required
def assignment_create(request):
    if request.method == 'POST':
        form = _assignment_form(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            assignment = form.save(commit=False)
            if request.user.role == 'teacher':
                assignment.teacher = _teacher_for_user(request.user)
            assignment.save()
            messages.success(request, 'Assignment created.')
            return redirect('assignment_list')
    else:
        form = _assignment_form(user=request.user)
    return render(request, 'assignments/assignment_form.html', {'form': form, 'title': 'Add Assignment'})


@teacher_or_admin_required
def assignment_update(request, pk):
    assignments = Assignment.objects.all()
    if request.user.role == 'teacher':
        assignments = assignments.filter(teacher__user=request.user)
    assignment = get_object_or_404(assignments, pk=pk)
    if request.method == 'POST':
        form = _assignment_form(request.POST, request.FILES, instance=assignment, user=request.user)
        if form.is_valid():
            assignment = form.save(commit=False)
            if request.user.role == 'teacher':
                assignment.teacher = _teacher_for_user(request.user)
            assignment.save()
            return redirect('assignment_list')
    else:
        form = _assignment_form(instance=assignment, user=request.user)
    return render(request, 'assignments/assignment_form.html', {'form': form, 'title': 'Edit Assignment'})


@teacher_or_admin_required
def assignment_delete(request, pk):
    assignments = Assignment.objects.all()
    if request.user.role == 'teacher':
        assignments = assignments.filter(teacher__user=request.user)
    assignment = get_object_or_404(assignments, pk=pk)
    if request.method == 'POST':
        assignment.delete()
        return redirect('assignment_list')
    return render(request, 'assignments/assignment_confirm_delete.html', {'object': assignment})


@login_required
def submit_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    student = Student.objects.filter(user=request.user).first()
    if not student:
        messages.error(request, 'Only students can submit assignments.')
        return redirect('my_assignments')

    if request.method == 'POST' and request.FILES.get('file'):
        Submission.objects.update_or_create(
            assignment=assignment, student=student,
            defaults={'file': request.FILES['file']}
        )
        messages.success(request, 'Assignment submitted successfully.')
    return redirect('my_assignments')
