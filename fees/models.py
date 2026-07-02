from django.db import models
from students.models import Student


class FeeCategory(models.Model):
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    semester = models.IntegerField()
    is_optional = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Fee Categories'

    def __str__(self):
        return f"{self.name} - {self.amount}"


class FeePayment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PAID = 'paid', 'Paid'
        PARTIAL = 'partial', 'Partially Paid'
        OVERDUE = 'overdue', 'Overdue'

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fee_payments')
    category = models.ForeignKey(FeeCategory, on_delete=models.CASCADE, related_name='payments')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    payment_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    receipt_number = models.CharField(max_length=50, unique=True, blank=True)
    payment_method = models.CharField(max_length=50, blank=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student} - {self.category} - {self.status}"
