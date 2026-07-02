from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Exam, Marks
from .forms import ExamForm
from students.models import Student
from teachers.models import Teacher
from accounts.decorators import admin_required, teacher_or_admin_required


@login_required
def exam_list(request):
    exams = Exam.objects.select_related('subject').all()
    return render(request, 'exams/exam_list.html', {'exams': exams})


@admin_required
def exam_create(request):
    if request.method == 'POST':
        form = ExamForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Exam created successfully.')
            return redirect('exam_list')
    else:
        form = ExamForm()
    return render(request, 'exams/exam_form.html', {'form': form, 'title': 'Add Exam'})


@admin_required
def exam_update(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    if request.method == 'POST':
        form = ExamForm(request.POST, instance=exam)
        if form.is_valid():
            form.save()
            return redirect('exam_list')
    else:
        form = ExamForm(instance=exam)
    return render(request, 'exams/exam_form.html', {'form': form, 'title': 'Edit Exam'})


@admin_required
def exam_delete(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    if request.method == 'POST':
        exam.delete()
        return redirect('exam_list')
    return render(request, 'exams/exam_confirm_delete.html', {'object': exam})


@teacher_or_admin_required
def upload_marks(request, exam_id):
    exams = Exam.objects.select_related('subject__teacher')
    if request.user.role == 'teacher':
        teacher = Teacher.objects.filter(user=request.user).first()
        exams = exams.filter(subject__teacher=teacher)
    exam = get_object_or_404(exams, pk=exam_id)
    students = Student.objects.filter(course=exam.subject.course, semester=exam.semester).select_related('user')

    if request.method == 'POST':
        for student in students:
            theory = int(request.POST.get(f'theory_{student.id}') or 0)
            practical = int(request.POST.get(f'practical_{student.id}') or 0)
            Marks.objects.update_or_create(
                student=student, exam=exam,
                defaults={'theory_marks': theory, 'practical_marks': practical}
            )
        messages.success(request, 'Marks uploaded successfully.')
        return redirect('exam_list')

    marks_data = {m.student_id: m for m in Marks.objects.filter(exam=exam)}
    return render(request, 'exams/upload_marks.html', {
        'exam': exam, 'students': students, 'marks_data': marks_data
    })
