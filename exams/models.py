from django.db import models
from students.models import Student
from subjects.models import Subject


class Exam(models.Model):
    class Type(models.TextChoices):
        INTERNAL = 'internal', 'Internal Exam'
        MID_SEM = 'mid_sem', 'Mid Semester'
        FINAL_SEM = 'final_sem', 'Final Semester'

    name = models.CharField(max_length=200)
    exam_type = models.CharField(max_length=20, choices=Type.choices)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='exams')
    semester = models.IntegerField()
    max_theory_marks = models.IntegerField(default=70)
    max_practical_marks = models.IntegerField(default=30)
    exam_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-exam_date']

    def __str__(self):
        return f"{self.name} - {self.subject}"


class Marks(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='marks')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='marks')
    theory_marks = models.IntegerField(default=0)
    practical_marks = models.IntegerField(default=0)
    total_marks = models.IntegerField(editable=False)
    grade = models.CharField(max_length=2, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['student', 'exam']
        verbose_name_plural = 'Marks'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        self.total_marks = self.theory_marks + self.practical_marks
        percentage = (self.total_marks / (self.exam.max_theory_marks + self.exam.max_practical_marks)) * 100
        if percentage >= 90:
            self.grade = 'A+'
        elif percentage >= 80:
            self.grade = 'A'
        elif percentage >= 70:
            self.grade = 'B+'
        elif percentage >= 60:
            self.grade = 'B'
        elif percentage >= 50:
            self.grade = 'C'
        elif percentage >= 40:
            self.grade = 'D'
        else:
            self.grade = 'F'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} - {self.exam} - {self.grade}"

    @property
    def percentage(self):
        max_total = self.exam.max_theory_marks + self.exam.max_practical_marks
        return round((self.total_marks / max_total) * 100, 2) if max_total else 0
