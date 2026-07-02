from django.shortcuts import render, redirect, get_object_or_404
from accounts.decorators import admin_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Teacher
from .forms import TeacherForm


@admin_required
def teacher_list(request):
    teachers = Teacher.objects.select_related('user', 'department').all()
    return render(request, 'teachers/teacher_list.html', {'teachers': teachers})


@admin_required
def teacher_create(request):
    if request.method == 'POST':
        form = TeacherForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Teacher created successfully.')
            return redirect('teacher_list')
    else:
        form = TeacherForm()
    return render(request, 'teachers/teacher_form.html', {'form': form, 'title': 'Add Teacher'})


@admin_required
def teacher_update(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == 'POST':
        form = TeacherForm(request.POST, instance=teacher)
        if form.is_valid():
            form.save()
            messages.success(request, 'Teacher updated successfully.')
            return redirect('teacher_list')
    else:
        initial = {'first_name': teacher.user.first_name, 'last_name': teacher.user.last_name, 'email': teacher.user.email}
        form = TeacherForm(instance=teacher, initial=initial)
    return render(request, 'teachers/teacher_form.html', {'form': form, 'title': 'Edit Teacher'})


@admin_required
def teacher_delete(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == 'POST':
        teacher.user.delete()
        teacher.delete()
        messages.success(request, 'Teacher deleted successfully.')
        return redirect('teacher_list')
    return render(request, 'teachers/teacher_confirm_delete.html', {'object': teacher})


@login_required
def teacher_classes(request):
    teacher = Teacher.objects.filter(user=request.user).first()
    if not teacher:
        messages.error(request, 'Teacher profile not found.')
        return redirect('dashboard')
    subjects = teacher.subjects.select_related('course').all()
    return render(request, 'teachers/my_classes.html', {'subjects': subjects})
