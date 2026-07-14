from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .middleware import get_current_user, get_current_ip
from .models import AuditLog

# Import audited models
from exams.models import Marks
from fees.models import FeePayment
from notices.models import Notice
from timetable.models import Timetable
from attendance.models import Attendance
from accounts.models import User


def record_audit(instance, action, details):
    user = get_current_user()
    ip = get_current_ip()
    AuditLog.objects.create(
        user=user,
        action=action,
        model_name=instance.__class__.__name__,
        object_id=instance.pk,
        details=details,
        ip_address=ip
    )


@receiver(post_save, sender=Marks)
def audit_marks_save(sender, instance, created, **kwargs):
    act = "Created Exam Marks" if created else "Updated Exam Marks"
    details = f"Student: {instance.student.user.get_full_name()} (Roll: {instance.student.roll_number}), Exam: {instance.exam.name}, Subject: {instance.exam.subject.name}, Marks: theory={instance.theory_marks}, practical={instance.practical_marks}, grade={instance.grade}"
    record_audit(instance, act, details)


@receiver(post_delete, sender=Marks)
def audit_marks_delete(sender, instance, **kwargs):
    details = f"Student: {instance.student.user.username}, Exam: {instance.exam.name}, Subject: {instance.exam.subject.name}"
    record_audit(instance, "Deleted Exam Marks", details)


@receiver(post_save, sender=FeePayment)
def audit_fee_payment_save(sender, instance, created, **kwargs):
    act = "Approved Fee Payment" if created else "Updated Fee Payment"
    details = f"Student: {instance.student.user.get_full_name()}, Category: {instance.category.name}, Amount: {instance.amount_paid}, Status: {instance.status}"
    record_audit(instance, act, details)


@receiver(post_save, sender=Notice)
def audit_notice_save(sender, instance, created, **kwargs):
    act = "Published Notice" if created else "Updated Notice"
    details = f"Title: {instance.title}, Priority: {instance.priority}, Active: {instance.is_active}"
    record_audit(instance, act, details)


@receiver(post_save, sender=Timetable)
def audit_timetable_save(sender, instance, created, **kwargs):
    act = "Created Timetable Slot" if created else "Updated Timetable Slot"
    details = f"Subject: {instance.subject.name}, Day: {instance.day}, Time: {instance.start_time}-{instance.end_time}, Room: {instance.room}"
    record_audit(instance, act, details)


@receiver(post_save, sender=Attendance)
def audit_attendance_save(sender, instance, created, **kwargs):
    act = "Marked Attendance" if created else "Updated Attendance"
    details = f"Student: {instance.student.user.get_full_name()}, Subject: {instance.subject.name}, Date: {instance.date}, Status: {instance.status}"
    record_audit(instance, act, details)


@receiver(post_save, sender=User)
def audit_user_save(sender, instance, created, **kwargs):
    current_user = get_current_user()
    if current_user:
        act = "Created User Credentials" if created else "Updated User Credentials"
        details = f"Username: {instance.username}, Role: {instance.role}, Email: {instance.email}"
        record_audit(instance, act, details)
