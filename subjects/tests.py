from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from students.models import Student
from courses.models import Course
from departments.models import Department
from timetable.models import Timetable
from .models import Subject, ElectiveEnrollment


class ElectiveChoiceSystemTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Setup Dept and Course
        self.dept = Department.objects.create(name='CS Dept', code='CSD')
        self.course = Course.objects.create(name='BTech CS', code='BTCS', department=self.dept, semester=8)
        
        # Setup Students
        self.user1 = User.objects.create_user(username='student1', password='password123', role='student')
        self.student1 = Student.objects.create(
            user=self.user1, course=self.course, semester=2, 
            admission_number='ADM001', roll_number='R001', batch='2023-27',
            date_of_birth='2002-05-10'
        )
        
        self.user2 = User.objects.create_user(username='student2', password='password123', role='student')
        self.student2 = Student.objects.create(
            user=self.user2, course=self.course, semester=2, 
            admission_number='ADM002', roll_number='R002', batch='2023-27',
            date_of_birth='2002-05-10'
        )
        
        # Setup Subjects
        self.elective = Subject.objects.create(
            name='Cloud Architecture', code='CS303', course=self.course, 
            semester=2, is_elective=True, max_capacity=1
        )
        self.core_subject = Subject.objects.create(
            name='Data Structures', code='CS201', course=self.course, 
            semester=2, is_elective=False
        )

        # Setup Teacher
        from teachers.models import Teacher
        self.teacher_user = User.objects.create_user(username='teacher_test', password='password123', role='teacher')
        self.teacher = Teacher.objects.create(
            user=self.teacher_user, employee_id='EMP999', department=self.dept, phone='12345'
        )

        # Setup Timetable slots
        self.elective_slot = Timetable.objects.create(
            department=self.dept, course=self.course, semester=2, day='monday',
            start_time='10:00', end_time='11:00', subject=self.elective, room='101',
            teacher=self.teacher
        )
        self.core_slot = Timetable.objects.create(
            department=self.dept, course=self.course, semester=2, day='monday',
            start_time='11:00', end_time='12:00', subject=self.core_subject, room='102',
            teacher=self.teacher
        )

    def test_electives_list_view(self):
        self.client.login(username='student1', password='password123')
        response = self.client.get(reverse('electives_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cloud Architecture')
        self.assertNotContains(response, 'Data Structures') # Core subjects shouldn't list as electives

    def test_enroll_elective_success(self):
        self.client.login(username='student1', password='password123')
        response = self.client.post(reverse('enroll_elective', args=[self.elective.id]))
        self.assertEqual(response.status_code, 302)
        
        # Check database record
        self.assertTrue(ElectiveEnrollment.objects.filter(student=self.student1, subject=self.elective).exists())

    def test_enroll_elective_capacity_limit(self):
        # Student 1 enrolls first
        self.client.login(username='student1', password='password123')
        self.client.post(reverse('enroll_elective', args=[self.elective.id]))
        
        # Student 2 tries to enroll but capacity is 1
        self.client.login(username='student2', password='password123')
        response = self.client.post(reverse('enroll_elective', args=[self.elective.id]))
        self.assertEqual(response.status_code, 302)
        
        # Check database: student 2 is NOT enrolled
        self.assertFalse(ElectiveEnrollment.objects.filter(student=self.student2, subject=self.elective).exists())

    def test_elective_withdrawal(self):
        # Enroll first
        ElectiveEnrollment.objects.create(student=self.student1, subject=self.elective)
        
        self.client.login(username='student1', password='password123')
        response = self.client.post(reverse('withdraw_elective', args=[self.elective.id]))
        self.assertEqual(response.status_code, 302)
        
        # Check database record is deleted
        self.assertFalse(ElectiveEnrollment.objects.filter(student=self.student1, subject=self.elective).exists())

    def test_timetable_filtering_based_on_elective_enrollment(self):
        self.client.login(username='student1', password='password123')
        
        # 1. Access timetable when NOT enrolled in elective
        response = self.client.get(reverse('my_timetable'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Data Structures')
        self.assertNotContains(response, 'Cloud Architecture') # Should filter out
        
        # 2. Enroll in elective and assert it appears in timetable
        ElectiveEnrollment.objects.create(student=self.student1, subject=self.elective)
        response = self.client.get(reverse('my_timetable'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Data Structures')
        self.assertContains(response, 'Cloud Architecture') # Appears now
