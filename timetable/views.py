from django.shortcuts import render, redirect, get_object_or_404
from accounts.decorators import admin_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Timetable
from .forms import TimetableForm


@login_required
def timetable_list(request):
    slots = Timetable.objects.select_related('course', 'subject', 'teacher').all()
    if request.user.role == 'teacher':
        slots = slots.filter(teacher__user=request.user)
    elif request.user.role == 'student':
        student = getattr(request.user, 'student_profile', None)
        if student:
            slots = slots.filter(course=student.course, semester=student.semester)
        else:
            slots = Timetable.objects.none()
    return render(request, 'timetable/timetable_list.html', {'slots': slots})


@admin_required
def timetable_create(request):
    if request.method == 'POST':
        form = TimetableForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Timetable slot created.')
            return redirect('timetable_list')
    else:
        form = TimetableForm()
    return render(request, 'timetable/timetable_form.html', {'form': form, 'title': 'Add Timetable Slot'})


@admin_required
def timetable_update(request, pk):
    slot = get_object_or_404(Timetable, pk=pk)
    if request.method == 'POST':
        form = TimetableForm(request.POST, instance=slot)
        if form.is_valid():
            form.save()
            return redirect('timetable_list')
    else:
        form = TimetableForm(instance=slot)
    return render(request, 'timetable/timetable_form.html', {'form': form, 'title': 'Edit Timetable Slot'})


@admin_required
def timetable_delete(request, pk):
    slot = get_object_or_404(Timetable, pk=pk)
    if request.method == 'POST':
        slot.delete()
        return redirect('timetable_list')
    return render(request, 'timetable/timetable_confirm_delete.html', {'object': slot})
