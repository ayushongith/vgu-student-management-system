from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from accounts.models import User
from departments.models import Department
from courses.models import Course
from subjects.models import Subject
from students.models import Student
from teachers.models import Teacher
from assignments.models import Assignment
from exams.models import Exam
from notices.models import Notice
from .models import Event
from datetime import date, timedelta


class CalendarAppTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(username='admin_test', email='admin@test.com', password='password', role='admin')
        self.teacher_user = User.objects.create_user(username='teacher_test', email='teacher@test.com', password='password', role='teacher')
        self.student_user = User.objects.create_user(username='student_test', email='student@test.com', password='password', role='student')
        
        self.dept = Department.objects.create(name='CSE', code='CS')
        self.course = Course.objects.create(name='B.Tech', code='BT', department=self.dept, semester=8, credits=4)
        
        self.teacher = Teacher.objects.create(user=self.teacher_user, employee_id='EMP101', department=self.dept, qualification='Ph.D')
        self.student = Student.objects.create(user=self.student_user, admission_number='ADM101', roll_number='R101', gender='male', date_of_birth=date(2002, 1, 1), department=self.dept, course=self.course, semester=1, batch='2023')
        self.subject = Subject.objects.create(name='Mathematics', code='MA101', course=self.course, teacher=self.teacher, credits=4)

    def test_calendar_page_requires_login(self):
        response = self.client.get(reverse('academic_calendar'))
        self.assertEqual(response.status_code, 302)

    def test_calendar_page_renders_for_logged_in_user(self):
        self.client.login(username='student_test', password='password')
        response = self.client.get(reverse('academic_calendar'))
        self.assertEqual(response.status_code, 200)

    def test_get_calendar_events_returns_all_types(self):
        Event.objects.create(
            title='VGU Fest',
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(hours=2),
            event_type='cultural',
            created_by=self.admin
        )
        
        Assignment.objects.create(
            title='Calculus homework',
            subject=self.subject,
            teacher=self.teacher,
            due_date=date.today() + timedelta(days=2),
            max_marks=10
        )
        
        Exam.objects.create(
            name='Algebra test',
            subject=self.subject,
            exam_type='mid_sem',
            semester=1,
            exam_date=date.today() + timedelta(days=5)
        )
        
        Notice.objects.create(
            title='Portal Updates',
            content='Maintenance tonight',
            posted_by=self.admin,
            is_active=True
        )

        self.client.login(username='student_test', password='password')
        response = self.client.get(reverse('get_calendar_events'))
        self.assertEqual(response.status_code, 200)
        
        events = response.json()
        self.assertGreaterEqual(len(events), 4)

        custom_ev = [ev for ev in events if ev['id'].startswith('custom_')][0]
        self.assertEqual(custom_ev['title'], 'VGU Fest')
        self.assertEqual(custom_ev['backgroundColor'], '#6f42c1')

        exam_ev = [ev for ev in events if ev['id'].startswith('exam_')][0]
        self.assertIn('Algebra test', exam_ev['title'])
        
        assign_ev = [ev for ev in events if ev['id'].startswith('assignment_')][0]
        self.assertIn('Calculus homework', assign_ev['title'])

    def test_create_custom_event_by_student_forbidden(self):
        self.client.login(username='student_test', password='password')
        response = self.client.post(reverse('create_calendar_event'), {
            'title': 'Secret party',
            'start_time': timezone.now().isoformat(),
            'end_time': (timezone.now() + timezone.timedelta(hours=1)).isoformat(),
            'event_type': 'cultural'
        })
        self.assertEqual(response.status_code, 403)

    def test_create_custom_event_by_teacher_success(self):
        self.client.login(username='teacher_test', password='password')
        start = timezone.now()
        end = start + timezone.timedelta(hours=1)
        
        response = self.client.post(reverse('create_calendar_event'), {
            'title': 'Guest Lecture',
            'description': 'On Neural Networks',
            'start_time': start.strftime('%Y-%m-%dT%H:%M'),
            'end_time': end.strftime('%Y-%m-%dT%H:%M'),
            'event_type': 'seminar'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        
        db_event = Event.objects.filter(title='Guest Lecture').first()
        self.assertIsNotNone(db_event)
        self.assertEqual(db_event.event_type, 'seminar')
        self.assertEqual(db_event.created_by, self.teacher_user)
