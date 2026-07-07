from django.db import models
from accounts.models import User


class Notification(models.Model):
    class Type(models.TextChoices):
        ASSIGNMENT = 'assignment', 'Assignment Alert'
        MARKS = 'marks', 'Exam Marks Uploaded'
        FEE = 'fee', 'Fee Payment Update'
        NOTICE = 'notice', 'Notice Board Announcement'

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    notification_type = models.CharField(max_length=20, choices=Type.choices)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} for {self.recipient.username}"
