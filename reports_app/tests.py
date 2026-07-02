from django.test import TestCase
from django.urls import reverse
from accounts.models import User

class ReportsAppTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin1', password='password', role='admin')
        self.teacher = User.objects.create_user(username='teacher1', password='password', role='teacher')

    def test_reports_dashboard_admin(self):
        self.client.login(username='admin1', password='password')
        response = self.client.get(reverse('reports_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_reports_dashboard_teacher_forbidden(self):
        self.client.login(username='teacher1', password='password')
        response = self.client.get(reverse('reports_dashboard'))
        self.assertEqual(response.status_code, 403)

    def test_attendance_report(self):
        self.client.login(username='admin1', password='password')
        response = self.client.get(reverse('attendance_report'))
        self.assertEqual(response.status_code, 200)

    def test_exam_report(self):
        self.client.login(username='admin1', password='password')
        response = self.client.get(reverse('exam_report'))
        self.assertEqual(response.status_code, 200)

    def test_fee_report(self):
        self.client.login(username='admin1', password='password')
        response = self.client.get(reverse('fee_report'))
        self.assertEqual(response.status_code, 200)
