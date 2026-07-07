from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Notification


@login_required
def notifications_list(request):
    notifications = Notification.objects.filter(recipient=request.user)
    return render(request, 'notifications/notifications_list.html', {
        'notifications': notifications
    })


@login_required
def mark_all_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    return redirect('notifications_list')
