from django.test import TestCase
from django.urls import reverse
from accounts.models import User
from students.models import Student
from departments.models import Department
from courses.models import Course
from .models import FeeCategory, FeePayment
from datetime import date

class FeeModelTests(TestCase):
    def setUp(self):
        self.category = FeeCategory.objects.create(name='Tuition Fee', amount=50000, semester=1)
        self.user = User.objects.create_user(username='student1', password='password', role='student', email='s1@test.com')
        self.dept = Department.objects.create(name='CS', code='CS101')
        self.course = Course.objects.create(name='B.Tech', code='BT', department=self.dept, semester=8)
        self.student = Student.objects.create(
            user=self.user, admission_number='A001', roll_number='R001',
            department=self.dept, course=self.course, semester=1, date_of_birth='2000-01-01'
        )

    def test_fee_category_creation(self):
        self.assertEqual(self.category.name, 'Tuition Fee')
        self.assertEqual(str(self.category), 'Tuition Fee - 50000')

    def test_fee_payment_creation(self):
        payment = FeePayment.objects.create(
            student=self.student, category=self.category,
            amount_paid=25000, due_date=date.today(), status='partial'
        )
        self.assertEqual(payment.status, 'partial')
        self.assertEqual(payment.amount_paid, 25000)

class FeeViewTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin1', password='password', role='admin', email='a@test.com')
        self.student_user = User.objects.create_user(username='student1', password='password', role='student', email='s@test.com')
        
        self.dept = Department.objects.create(name='CS', code='CS101')
        self.course = Course.objects.create(name='B.Tech', code='BT', department=self.dept, semester=8)
        self.student = Student.objects.create(
            user=self.student_user, admission_number='A001', roll_number='R001',
            department=self.dept, course=self.course, semester=1, date_of_birth='2000-01-01'
        )
        
        self.category = FeeCategory.objects.create(name='Library Fee', amount=1000, semester=1)
        self.payment = FeePayment.objects.create(
            student=self.student, category=self.category,
            amount_paid=1000, due_date=date.today(), status='paid'
        )

    def test_fee_list_view_for_admin(self):
        self.client.login(username='admin1', password='password')
        response = self.client.get(reverse('fee_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Library Fee')

    def test_fee_list_view_for_student(self):
        self.client.login(username='student1', password='password')
        response = self.client.get(reverse('fee_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Library Fee')

    def test_fee_category_create_view(self):
        self.client.login(username='admin1', password='password')
        response = self.client.post(reverse('fee_category_create'), {
            'name': 'Hostel Fee', 'amount': 15000, 'semester': 1
        })
        self.assertEqual(response.status_code, 302)  # Redirects after success
        self.assertTrue(FeeCategory.objects.filter(name='Hostel Fee').exists())

    def test_student_cannot_create_category(self):
        self.client.login(username='student1', password='password')
        response = self.client.post(reverse('fee_category_create'), {
            'name': 'Hostel Fee', 'amount': 15000, 'semester': 1
        })
        self.assertEqual(response.status_code, 403)  # Admin required
