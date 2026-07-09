from django.test import TestCase
from django.urls import reverse
from accounts.models import User
from students.models import Student
from departments.models import Department
from courses.models import Course
from datetime import date

class ReportsAppTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin1', password='password', role='admin')
        self.teacher = User.objects.create_user(username='teacher1', password='password', role='teacher')
        self.student_user1 = User.objects.create_user(username='student_u1', password='password', role='student')
        self.student_user2 = User.objects.create_user(username='student_u2', password='password', role='student')
        
        self.dept = Department.objects.create(name='CSE', code='CS')
        self.course = Course.objects.create(name='B.Tech', code='BT', department=self.dept, semester=8, credits=4)
        
        self.student1 = Student.objects.create(
            user=self.student_user1, admission_number='ADM1', roll_number='R1', gender='male',
            date_of_birth=date(2002, 1, 1), department=self.dept, course=self.course, semester=1, batch='2023'
        )
        self.student2 = Student.objects.create(
            user=self.student_user2, admission_number='ADM2', roll_number='R2', gender='female',
            date_of_birth=date(2002, 1, 1), department=self.dept, course=self.course, semester=1, batch='2023'
        )

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

    def test_academic_predictor_student_self_access(self):
        self.client.login(username='student_u1', password='password')
        response = self.client.get(reverse('academic_predictor'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Academic Advisor & Predictor')

    def test_academic_predictor_student_other_forbidden(self):
        self.client.login(username='student_u1', password='password')
        # Trying to access student2 details directly via detail URL
        response = self.client.get(reverse('academic_predictor_detail', args=[self.student2.pk]))
        self.assertEqual(response.status_code, 403)

    def test_academic_predictor_admin_any_access(self):
        self.client.login(username='admin1', password='password')
        response = self.client.get(reverse('academic_predictor_detail', args=[self.student2.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Academic Advisor & Predictor')

    def test_download_transcript_student_self(self):
        self.client.login(username='student_u1', password='password')
        response = self.client.get(reverse('download_student_transcript'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/pdf')
        # Check PDF signature
        pdf_content = b''.join(response.streaming_content)
        self.assertTrue(pdf_content.startswith(b'%PDF-'))

    def test_download_transcript_student_other_forbidden(self):
        self.client.login(username='student_u1', password='password')
        response = self.client.get(reverse('download_transcript', args=[self.student2.pk]))
        self.assertEqual(response.status_code, 403)

    def test_download_transcript_admin(self):
        self.client.login(username='admin1', password='password')
        response = self.client.get(reverse('download_transcript', args=[self.student2.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/pdf')
        pdf_content = b''.join(response.streaming_content)
        self.assertTrue(pdf_content.startswith(b'%PDF-'))

