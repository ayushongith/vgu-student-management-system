from django.test import TestCase
from django.urls import reverse
from accounts.models import User
from students.models import Student
from teachers.models import Teacher
from departments.models import Department
from courses.models import Course
from subjects.models import Subject
from .models import Timetable
from datetime import time

class TimetableTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin1', password='password', role='admin')
        self.teacher_user = User.objects.create_user(username='teacher1', password='password', role='teacher')
        self.student_user = User.objects.create_user(username='student1', password='password', role='student')
        
        self.dept = Department.objects.create(name='CS', code='CS101')
        self.course = Course.objects.create(name='B.Tech', code='BT', department=self.dept, semester=8)
        self.teacher = Teacher.objects.create(user=self.teacher_user, department=self.dept, employee_id='E001')
        self.subject = Subject.objects.create(name='Math', code='M1', course=self.course, teacher=self.teacher)
        self.student = Student.objects.create(
            user=self.student_user, admission_number='A001', roll_number='R001',
            department=self.dept, course=self.course, semester=1, date_of_birth='2000-01-01'
        )
        
        self.timetable = Timetable.objects.create(
            department=self.dept, course=self.course, semester=1,
            day='monday', start_time=time(10, 0), end_time=time(11, 0),
            subject=self.subject, teacher=self.teacher, room='101'
        )

    def test_timetable_creation(self):
        self.assertEqual(str(self.timetable), f"{self.course} - monday 10:00:00-11:00:00")

    def test_timetable_list_admin(self):
        self.client.login(username='admin1', password='password')
        response = self.client.get(reverse('timetable_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Math')

    def test_timetable_list_student(self):
        self.client.login(username='student1', password='password')
        response = self.client.get(reverse('timetable_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Math')
        
    def test_timetable_create_admin(self):
        self.client.login(username='admin1', password='password')
        response = self.client.post(reverse('timetable_create'), {
            'department': self.dept.id, 'course': self.course.id, 'semester': 1,
            'day': 'tuesday', 'start_time': '12:00:00', 'end_time': '13:00:00',
            'subject': self.subject.id, 'teacher': self.teacher.id, 'room': '102',
            'is_active': True
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Timetable.objects.filter(day='tuesday').exists())
