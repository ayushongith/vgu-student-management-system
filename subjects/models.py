from django.db import models
from courses.models import Course
from teachers.models import Teacher


class Subject(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='subjects')
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name='subjects')
    credits = models.IntegerField(default=4)
    is_active = models.BooleanField(default=True)
    is_elective = models.BooleanField(default=False)
    max_capacity = models.IntegerField(default=60)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['course', 'name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class ElectiveEnrollment(models.Model):
    from students.models import Student
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='elective_enrollments')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'subject')

    def __str__(self):
        return f"{self.student.user.username} enrolled in {self.subject.name}"
