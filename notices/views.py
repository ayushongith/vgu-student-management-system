from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.decorators import admin_required
from django.contrib import messages
from .models import Notice
from .forms import NoticeForm


@login_required
def notice_list(request):
    notices = Notice.objects.filter(is_active=True)
    return render(request, 'notices/notice_list.html', {'notices': notices})


@admin_required
def notice_create(request):
    if request.method == 'POST':
        form = NoticeForm(request.POST, request.FILES)
        if form.is_valid():
            notice = form.save(commit=False)
            notice.posted_by = request.user
            notice.save()
            messages.success(request, 'Notice published.')
            return redirect('notice_list')
    else:
        form = NoticeForm()
    return render(request, 'notices/notice_form.html', {'form': form, 'title': 'Create Notice'})


@admin_required
def notice_update(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    if request.method == 'POST':
        form = NoticeForm(request.POST, request.FILES, instance=notice)
        if form.is_valid():
            form.save()
            return redirect('notice_list')
    else:
        form = NoticeForm(instance=notice)
    return render(request, 'notices/notice_form.html', {'form': form, 'title': 'Edit Notice'})


@admin_required
def notice_delete(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    if request.method == 'POST':
        notice.delete()
        return redirect('notice_list')
    return render(request, 'notices/notice_confirm_delete.html', {'object': notice})
