from django.db import models
from accounts.models import User
from departments.models import Department
from courses.models import Course


class Student(models.Model):
    class Gender(models.TextChoices):
        MALE = 'male', 'Male'
        FEMALE = 'female', 'Female'
        OTHER = 'other', 'Other'

    class BloodGroup(models.TextChoices):
        A_POS = 'A+', 'A+'
        A_NEG = 'A-', 'A-'
        B_POS = 'B+', 'B+'
        B_NEG = 'B-', 'B-'
        AB_POS = 'AB+', 'AB+'
        AB_NEG = 'AB-', 'AB-'
        O_POS = 'O+', 'O+'
        O_NEG = 'O-', 'O-'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    admission_number = models.CharField(max_length=20, unique=True)
    roll_number = models.CharField(max_length=20, unique=True)
    gender = models.CharField(max_length=10, choices=Gender.choices)
    date_of_birth = models.DateField()
    blood_group = models.CharField(max_length=5, choices=BloodGroup.choices, blank=True)
    phone = models.CharField(max_length=15)
    parent_name = models.CharField(max_length=200)
    parent_contact = models.CharField(max_length=15)
    address = models.TextField()
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='students')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, related_name='students')
    semester = models.IntegerField(default=1)
    batch = models.CharField(max_length=20)
    admission_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['roll_number']

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.admission_number})"

    @property
    def name(self):
        return self.user.get_full_name()

    @property
    def email(self):
        return self.user.email
