from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpResponse, JsonResponse, Http404
from django.template.loader import render_to_string
from accounts.models import User
from students.models import Student
from teachers.models import Teacher
from subjects.models import Subject
from .models import ForumThread, ForumPost
from .forms import ThreadForm, PostForm


def get_user_subjects(user):
    if user.role == 'admin':
        return Subject.objects.all().select_related('course')
    elif user.role == 'teacher':
        teacher = Teacher.objects.filter(user=user).first()
        if not teacher:
            return Subject.objects.none()
        return Subject.objects.filter(teacher=teacher).select_related('course')
    elif user.role == 'student':
        student = Student.objects.filter(user=user).first()
        if not student or not student.course:
            return Subject.objects.none()
        return Subject.objects.filter(course=student.course).select_related('course')
    return Subject.objects.none()


@login_required
def forum_list(request):
    subjects = get_user_subjects(request.user).annotate(thread_count=Count('threads'))
    
    # Optional: fetch the latest 5 threads across any of the user's subjects
    latest_threads = ForumThread.objects.filter(subject__in=subjects).select_related('subject', 'author').order_by('-created_at')[:5]
    
    return render(request, 'forums/forum_list.html', {
        'subjects': subjects,
        'latest_threads': latest_threads
    })


@login_required
def subject_threads(request, subject_id):
    subjects = get_user_subjects(request.user)
    subject = get_object_or_404(subjects, pk=subject_id)
    threads = ForumThread.objects.filter(subject=subject).select_related('author').order_by('-created_at')
    
    return render(request, 'forums/subject_threads.html', {
        'subject': subject,
        'threads': threads
    })


@login_required
def thread_detail(request, thread_id):
    subjects = get_user_subjects(request.user)
    thread = get_object_or_404(ForumThread.objects.filter(subject__in=subjects).select_related('subject', 'author'), pk=thread_id)
    
    # Handle AJAX poll requests
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        posts = ForumPost.objects.filter(thread=thread).select_related('author')
        html = render_to_string('forums/posts_list_partial.html', {'posts': posts, 'user': request.user})
        return HttpResponse(html)

    posts = ForumPost.objects.filter(thread=thread).select_related('author')
    
    if request.method == 'POST':
        form = PostForm(request.method == 'POST' or None, data=request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.thread = thread
            post.author = request.user
            post.save()
            return redirect('thread_detail', thread_id=thread.pk)
    else:
        form = PostForm()
        
    return render(request, 'forums/thread_detail.html', {
        'thread': thread,
        'posts': posts,
        'form': form
    })


@login_required
def create_thread(request, subject_id):
    subjects = get_user_subjects(request.user)
    subject = get_object_or_404(subjects, pk=subject_id)
    
    if request.method == 'POST':
        form = ThreadForm(request.POST)
        if form.is_valid():
            thread = form.save(commit=False)
            thread.subject = subject
            thread.author = request.user
            thread.save()
            return redirect('subject_threads', subject_id=subject.pk)
    else:
        form = ThreadForm()
        
    return render(request, 'forums/thread_form.html', {
        'subject': subject,
        'form': form
    })
