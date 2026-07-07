from django.test import TestCase, Client
from django.urls import reverse
from django.core import mail
from accounts.models import User
from departments.models import Department
from courses.models import Course
from subjects.models import Subject
from students.models import Student
from teachers.models import Teacher
from assignments.models import Assignment
from exams.models import Exam, Marks
from notices.models import Notice
from .models import Notification
from datetime import date


class NotificationsAppTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        self.admin = User.objects.create_superuser(username='admin_test', email='admin@test.com', password='password', role='admin')
        self.teacher_user = User.objects.create_user(username='teacher_test', email='teacher@test.com', password='password', role='teacher')
        self.student_user = User.objects.create_user(username='student_test', email='student@test.com', password='password', role='student')
        
        self.dept = Department.objects.create(name='CSE', code='CS')
        self.course = Course.objects.create(name='B.Tech', code='BT', department=self.dept, semester=8, credits=4)
        
        self.teacher = Teacher.objects.create(user=self.teacher_user, employee_id='EMP999', department=self.dept, qualification='Ph.D')
        self.student = Student.objects.create(user=self.student_user, admission_number='ADM999', roll_number='R999', gender='male', date_of_birth=date(2002, 1, 1), department=self.dept, course=self.course, semester=1, batch='2023')
        
        self.subject = Subject.objects.create(name='Mathematics', code='MA101', course=self.course, teacher=self.teacher, credits=4)

    def test_assignment_signal_creates_notifications(self):
        mail.outbox = []
        
        assignment = Assignment.objects.create(
            title='Calculus Homework',
            description='Solve exercises 1 to 5',
            subject=self.subject,
            teacher=self.teacher,
            due_date=date(2026, 8, 1),
            max_marks=10
        )
        
        notification = Notification.objects.filter(recipient=self.student_user, notification_type='assignment').first()
        self.assertIsNotNone(notification)
        self.assertEqual(notification.title, "New Assignment: Calculus Homework")
        
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("New Assignment: Calculus Homework", mail.outbox[0].subject)

    def test_marks_signal_creates_notification(self):
        mail.outbox = []
        exam = Exam.objects.create(name='Algebra Midterm', subject=self.subject, exam_type='mid_sem', semester=1)
        
        Marks.objects.create(
            student=self.student,
            exam=exam,
            theory_marks=40,
            practical_marks=20
        )
        
        notification = Notification.objects.filter(recipient=self.student_user, notification_type='marks').first()
        self.assertIsNotNone(notification)
        self.assertIn("Grades Posted", notification.title)
        
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Grades Uploaded: Algebra Midterm", mail.outbox[0].subject)

    def test_high_priority_notice_notifies_all(self):
        mail.outbox = []
        Notice.objects.create(
            title='Exam Schedule Out',
            content='Algebra exams start tomorrow.',
            posted_by=self.admin,
            priority='high',
            is_active=True
        )
        
        self.assertTrue(Notification.objects.filter(recipient=self.student_user, notification_type='notice').exists())
        self.assertTrue(Notification.objects.filter(recipient=self.admin, notification_type='notice').exists())
        
        self.assertGreater(len(mail.outbox), 0)

    def test_mark_all_read_view(self):
        Notification.objects.create(
            recipient=self.student_user,
            title='Alert',
            message='Test Alert',
            notification_type='notice'
        )
        
        self.client.login(username='student_test', password='password')
        response = self.client.get(reverse('mark_all_read'))
        self.assertEqual(response.status_code, 302)
        
        unread = Notification.objects.filter(recipient=self.student_user, is_read=False).count()
        self.assertEqual(unread, 0)
