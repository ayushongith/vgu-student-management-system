from django.test import TestCase
from django.urls import reverse
from accounts.models import User
from students.models import Student
from teachers.models import Teacher
from departments.models import Department
from courses.models import Course
from subjects.models import Subject
from .models import Assignment, Submission
from datetime import date

class AssignmentTests(TestCase):
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
        
        self.assignment = Assignment.objects.create(
            title='Homework 1', description='Solve equations',
            subject=self.subject, teacher=self.teacher,
            due_date=date.today(), max_marks=10
        )

    def test_assignment_creation(self):
        self.assertEqual(str(self.assignment), 'Homework 1')

    def test_submission_creation(self):
        submission = Submission.objects.create(
            assignment=self.assignment, student=self.student,
            feedback='Done', marks_obtained=9
        )
        self.assertEqual(str(submission), f"{self.student} - Homework 1")

    def test_assignment_list_teacher(self):
        self.client.login(username='teacher1', password='password')
        response = self.client.get(reverse('assignment_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Homework 1')

    def test_student_my_assignments(self):
        self.client.login(username='student1', password='password')
        response = self.client.get(reverse('my_assignments'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Homework 1')
