from django.db import models
from accounts.models import User


class Event(models.Model):
    class Type(models.TextChoices):
        HOLIDAY = 'holiday', 'Official Holiday'
        EXAM = 'exam', 'Exam Schedule'
        SEMINAR = 'seminar', 'Academic Seminar'
        CULTURAL = 'cultural', 'Cultural Event / Fest'
        OTHER = 'other', 'Other Event'

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    event_type = models.CharField(max_length=20, choices=Type.choices, default=Type.OTHER)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_events')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['start_time']

    def __str__(self):
        return self.title
