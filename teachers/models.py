from django.db import models
from accounts.models import User
from departments.models import Department


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='teachers')
    qualification = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    address = models.TextField(blank=True)
    date_joined = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['user__first_name']

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"

    @property
    def name(self):
        return self.user.get_full_name()

    @property
    def email(self):
        return self.user.email
