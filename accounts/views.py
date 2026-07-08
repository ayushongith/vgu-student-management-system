from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm, UserProfileForm, CustomPasswordChangeForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name()}!')
            return redirect('dashboard')
        messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


@login_required
def profile_view(request):
    user = request.user
    role = user.role
    sub_profile = None
    sub_form = None
    
    if role == 'student':
        from students.models import Student
        from .forms import StudentProfileUpdateForm
        sub_profile = Student.objects.filter(user=user).select_related('course', 'department').first()
        if sub_profile:
            sub_form_class = StudentProfileUpdateForm
        else:
            sub_form_class = None
    elif role == 'teacher':
        from teachers.models import Teacher
        from .forms import TeacherProfileUpdateForm
        sub_profile = Teacher.objects.filter(user=user).select_related('department').first()
        if sub_profile:
            sub_form_class = TeacherProfileUpdateForm
        else:
            sub_form_class = None
    else:
        sub_form_class = None

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if sub_profile and sub_form_class:
            sub_form = sub_form_class(request.POST, instance=sub_profile)
        else:
            sub_form = None
            
        forms_valid = form.is_valid()
        if sub_form:
            forms_valid = forms_valid and sub_form.is_valid()
            
        if forms_valid:
            form.save()
            if sub_form:
                sub_form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user)
        if sub_profile and sub_form_class:
            sub_form = sub_form_class(instance=sub_profile)

    return render(request, 'accounts/profile.html', {
        'form': form,
        'sub_form': sub_form,
        'sub_profile': sub_profile,
    })


@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully.')
            return redirect('profile')
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {'form': form})
