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
