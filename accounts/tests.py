from datetime import date, time, timedelta

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from accounts.models import User
from assignments.models import Assignment
from attendance.models import Attendance
from courses.models import Course
from departments.models import Department
from exams.models import Exam, Marks
from fees.models import FeeCategory, FeePayment
from notices.models import Notice
from students.models import Student
from subjects.models import Subject
from teachers.models import Teacher
from timetable.models import Timetable


class ProjectSmokeTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin',
            password='StrongPass123!',
            role='admin',
            first_name='Admin',
            last_name='User',
        )
        self.teacher_user = User.objects.create_user(
            username='teacher',
            password='StrongPass123!',
            role='teacher',
            first_name='Teacher',
            last_name='User',
        )
        self.student_user = User.objects.create_user(
            username='student',
            password='StrongPass123!',
            role='student',
            first_name='Student',
            last_name='User',
        )
        self.department = Department.objects.create(name='Computer Science', code='CS')
        self.course = Course.objects.create(
            name='MCA', code='MCA', department=self.department, semester=1
        )
        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            employee_id='T001',
            department=self.department,
            qualification='M.Tech',
            phone='9999999999',
        )
        self.student = Student.objects.create(
            user=self.student_user,
            admission_number='A001',
            roll_number='R001',
            gender='male',
            date_of_birth='2000-01-01',
            phone='8888888888',
            parent_name='Parent',
            parent_contact='7777777777',
            address='Address',
            department=self.department,
            course=self.course,
            semester=1,
            batch='2026',
        )
        self.subject = Subject.objects.create(
            name='Python', code='PY101', course=self.course, teacher=self.teacher
        )
        self.attendance = Attendance.objects.create(
            student=self.student,
            subject=self.subject,
            date=date.today(),
            status='present',
            marked_by=self.teacher,
        )
        self.exam = Exam.objects.create(
            name='Internal 1',
            exam_type='internal',
            subject=self.subject,
            semester=1,
            exam_date=date.today(),
        )
        self.marks = Marks.objects.create(
            student=self.student,
            exam=self.exam,
            theory_marks=40,
            practical_marks=20,
        )
        self.timetable = Timetable.objects.create(
            department=self.department,
            course=self.course,
            semester=1,
            day='monday',
            start_time=time(9, 0),
            end_time=time(10, 0),
            subject=self.subject,
            teacher=self.teacher,
            room='101',
        )
        self.assignment = Assignment.objects.create(
            title='Assignment 1',
            description='Complete exercise',
            subject=self.subject,
            teacher=self.teacher,
            due_date=date.today() + timedelta(days=7),
        )
        self.notice = Notice.objects.create(
            title='Welcome',
            content='Welcome students',
            posted_by=self.admin_user,
        )
        self.fee_category = FeeCategory.objects.create(
            name='Tuition',
            amount=1000,
            semester=1,
        )
        self.fee_payment = FeePayment.objects.create(
            student=self.student,
            category=self.fee_category,
            amount_paid=1000,
            due_date=date.today(),
            payment_date=date.today(),
            status='paid',
        )

    def assert_get_ok(self, url_name, user, args=None, query=''):
        self.client.force_login(user)
        url = reverse(url_name, args=args or [])
        response = self.client.get(f'{url}{query}')
        self.assertEqual(response.status_code, 200, url_name)

    def test_admin_main_pages_render_for_role_admin_without_staff_flag(self):
        pages = [
            ('dashboard', None),
            ('student_list', None),
            ('student_detail', [self.student.id]),
            ('teacher_list', None),
            ('department_list', None),
            ('course_list', None),
            ('subject_list', None),
            ('attendance_list', None),
            ('exam_list', None),
            ('timetable_list', None),
            ('assignment_list', None),
            ('notice_list', None),
            ('fee_list', None),
            ('fee_category_list', None),
            ('reports_dashboard', None),
            ('attendance_report', None),
            ('exam_report', None),
            ('fee_report', None),
            ('export_students_csv', None),
        ]

        for url_name, args in pages:
            self.assert_get_ok(url_name, self.admin_user, args=args)

    def test_teacher_main_pages_render(self):
        for url_name in [
            'dashboard',
            'teacher_classes',
            'attendance_list',
            'exam_list',
            'timetable_list',
            'assignment_list',
            'notice_list',
        ]:
            self.assert_get_ok(url_name, self.teacher_user)
        self.assert_get_ok('upload_marks', self.teacher_user, args=[self.exam.id])

    def test_student_main_pages_render(self):
        for url_name in [
            'dashboard',
            'my_attendance',
            'my_marks',
            'my_timetable',
            'my_assignments',
            'notice_list',
            'fee_list',
        ]:
            self.assert_get_ok(url_name, self.student_user)

    def test_api_list_endpoints_render_for_authenticated_user(self):
        client = APIClient()
        client.force_authenticate(user=self.admin_user)
        for path in [
            '/api/students/',
            '/api/teachers/',
            '/api/departments/',
            '/api/courses/',
            '/api/subjects/',
            '/api/attendance/',
            '/api/exams/',
            '/api/marks/',
            '/api/timetable/',
            '/api/assignments/',
            '/api/notices/',
            '/api/fees/',
        ]:
            response = client.get(path)
            self.assertEqual(response.status_code, 200, path)

    def test_student_can_update_profile(self):
        self.client.force_login(self.student_user)
        response = self.client.post(reverse('profile'), {
            'first_name': 'NewStudentName',
            'last_name': 'User',
            'email': 'newstudent@test.com',
            'phone': '12345',
            'gender': 'female',
            'date_of_birth': '2001-05-15',
            'parent_name': 'NewParent',
            'parent_contact': '999',
            'address': 'NewAddress'
        })
        self.assertEqual(response.status_code, 302)
        # Refresh and assert
        self.student_user.refresh_from_db()
        self.student.refresh_from_db()
        self.assertEqual(self.student_user.first_name, 'NewStudentName')
        self.assertEqual(self.student_user.email, 'newstudent@test.com')
        self.assertEqual(self.student.gender, 'female')
        self.assertEqual(self.student.parent_name, 'NewParent')
        self.assertEqual(self.student.address, 'NewAddress')

    def test_teacher_can_update_profile(self):
        self.client.force_login(self.teacher_user)
        response = self.client.post(reverse('profile'), {
            'first_name': 'NewTeacherName',
            'last_name': 'User',
            'email': 'newteacher@test.com',
            'phone': '54321',
            'qualification': 'PhD Computer Science',
            'address': 'NewTeacherAddress'
        })
        self.assertEqual(response.status_code, 302)
        # Refresh and assert
        self.teacher_user.refresh_from_db()
        self.teacher.refresh_from_db()
        self.assertEqual(self.teacher_user.first_name, 'NewTeacherName')
        self.assertEqual(self.teacher_user.email, 'newteacher@test.com')
        self.assertEqual(self.teacher.qualification, 'PhD Computer Science')
        self.assertEqual(self.teacher.address, 'NewTeacherAddress')

    def test_profile_photo_cleanup_on_delete_and_change(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        import os
        
        photo = SimpleUploadedFile("avatar.jpg", b"file_content", content_type="image/jpeg")
        user = User.objects.create_user(
            username='temp_user',
            password='password123',
            profile_photo=photo
        )
        
        photo_path = user.profile_photo.path
        self.assertTrue(os.path.exists(photo_path))

        new_photo = SimpleUploadedFile("avatar2.jpg", b"new_file_content", content_type="image/jpeg")
        user.profile_photo = new_photo
        user.save()
        
        self.assertFalse(os.path.exists(photo_path))
        new_photo_path = user.profile_photo.path
        self.assertTrue(os.path.exists(new_photo_path))
        
        user.delete()
        self.assertFalse(os.path.exists(new_photo_path))
