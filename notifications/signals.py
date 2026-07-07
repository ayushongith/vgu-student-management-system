from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from assignments.models import Assignment
from exams.models import Marks
from fees.models import FeePayment
from notices.models import Notice
from students.models import Student
from accounts.models import User
from .models import Notification


@receiver(post_save, sender=Assignment)
def notify_new_assignment(sender, instance, created, **kwargs):
    if created:
        subject = instance.subject
        course = subject.course
        students = Student.objects.filter(course=course).select_related('user')
        
        recipients = []
        for student in students:
            Notification.objects.create(
                recipient=student.user,
                title=f"New Assignment: {instance.title}",
                message=f"A new assignment has been uploaded for {subject.name}. Due Date: {instance.due_date.strftime('%d %b %Y')}. Max Marks: {instance.max_marks}",
                notification_type=Notification.Type.ASSIGNMENT
            )
            if student.user.email:
                recipients.append(student.user.email)
                
        if recipients:
            send_mail(
                subject=f"VGU Portal Alert - New Assignment: {instance.title}",
                message=f"Dear Student,\n\nA new assignment '{instance.title}' has been uploaded for the subject '{subject.name}'.\nDue Date: {instance.due_date}\nMax Marks: {instance.max_marks}\n\nPlease log in to the portal to view details and submit.\n\nVGU Administrative Desk",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipients,
                fail_silently=True
            )


@receiver(post_save, sender=Marks)
def notify_marks_uploaded(sender, instance, created, **kwargs):
    student = instance.student
    exam = instance.exam
    subject = exam.subject
    
    Notification.objects.create(
        recipient=student.user,
        title=f"Grades Posted: {exam.name}",
        message=f"Your grades for the exam '{exam.name}' have been uploaded. Score: {instance.total_marks} / {exam.max_theory_marks + exam.max_practical_marks}. Grade: {instance.grade}.",
        notification_type=Notification.Type.MARKS
    )
    
    if student.user.email:
        send_mail(
            subject=f"VGU Portal Alert - Grades Uploaded: {exam.name}",
            message=f"Dear {student.user.get_full_name() or student.user.username},\n\nYour grades for the exam '{exam.name}' under subject '{subject.name}' have been uploaded.\n\nMarks Obtained: {instance.total_marks} (Theory: {instance.theory_marks}, Practical: {instance.practical_marks})\nGrade: {instance.grade}\n\nPlease check your Student Dashboard for more details.\n\nVGU Examination Office",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[student.user.email],
            fail_silently=True
        )


@receiver(post_save, sender=FeePayment)
def notify_fee_payment_update(sender, instance, created, **kwargs):
    student = instance.student
    category = instance.category
    
    if instance.status in ['paid', 'partial']:
        Notification.objects.create(
            recipient=student.user,
            title="Fee Payment Update",
            message=f"A payment of INR {instance.amount_paid} has been registered for '{category.name}'. Current Status: {instance.get_status_display()}.",
            notification_type=Notification.Type.FEE
        )
        
        if student.user.email:
            send_mail(
                subject="VGU Portal Alert - Fee Payment Confirmation",
                message=f"Dear Student,\n\nWe have received and registered a payment of INR {instance.amount_paid} for the fee category '{category.name}' (Receipt: {instance.receipt_number}).\n\nTransaction Details:\nCategory: {category.name}\nAmount Paid: INR {instance.amount_paid}\nPayment Status: {instance.get_status_display()}\n\nThank you,\nVGU Accounts Branch",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[student.user.email],
                fail_silently=True
            )


@receiver(post_save, sender=Notice)
def notify_high_priority_notice(sender, instance, created, **kwargs):
    if created and instance.priority == 'high' and instance.is_active:
        users = User.objects.filter(is_active=True)
        
        recipients = []
        for user in users:
            Notification.objects.create(
                recipient=user,
                title=f"Urgent Notice: {instance.title}",
                message=instance.content,
                notification_type=Notification.Type.NOTICE
            )
            if user.email:
                recipients.append(user.email)
                
        if recipients:
            send_mail(
                subject=f"URGENT: VGU Notice Board - {instance.title}",
                message=f"Administrative Notice:\n\nTitle: {instance.title}\n\nAnnouncement Details:\n{instance.content}\n\nPosted By: {instance.posted_by.get_full_name() or instance.posted_by.username}\n\nPlease check the online Notice Board for updates.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipients,
                fail_silently=True
            )
