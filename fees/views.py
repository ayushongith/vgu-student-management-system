from django.shortcuts import render, redirect, get_object_or_404
from accounts.decorators import admin_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import FeeCategory, FeePayment
from .forms import FeeCategoryForm, FeePaymentForm
from students.models import Student


@login_required
def fee_list(request):
    if request.user.role == 'student':
        student = Student.objects.filter(user=request.user).first()
        payments = FeePayment.objects.filter(student=student).select_related('category') if student else FeePayment.objects.none()
    else:
        payments = FeePayment.objects.select_related('student__user', 'category').all()
    return render(request, 'fees/fee_list.html', {'payments': payments})


@admin_required
def fee_payment_create(request):
    if request.method == 'POST':
        form = FeePaymentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Payment recorded.')
            return redirect('fee_list')
    else:
        form = FeePaymentForm()
    return render(request, 'fees/fee_form.html', {'form': form, 'title': 'Record Payment'})


@admin_required
def fee_category_list(request):
    categories = FeeCategory.objects.all()
    return render(request, 'fees/fee_category_list.html', {'categories': categories})


@admin_required
def fee_category_create(request):
    if request.method == 'POST':
        form = FeeCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('fee_category_list')
    else:
        form = FeeCategoryForm()
    return render(request, 'fees/fee_form.html', {'form': form, 'title': 'Add Fee Category'})
