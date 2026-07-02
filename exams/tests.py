from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from courses.models import Course
from departments.models import Department
from exams.models import Exam, Marks
from students.models import Student
from subjects.models import Subject
from teachers.models import Teacher


class MarksUploadPermissionTests(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name='Computer Science', code='CS')
        self.course = Course.objects.create(
            name='MCA', code='MCA', department=self.department, semester=1
        )
        self.teacher_user = User.objects.create_user(
            username='teacher', password='pass12345', role='teacher'
        )
        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            employee_id='T001',
            department=self.department,
            qualification='MCA',
            phone='9999999999',
        )
        self.student_user = User.objects.create_user(
            username='student', password='pass12345', role='student'
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
        self.exam = Exam.objects.create(
            name='Internal 1',
            exam_type='internal',
            subject=self.subject,
            semester=1,
        )

    def test_student_cannot_upload_marks(self):
        self.client.force_login(self.student_user)
        response = self.client.post(reverse('upload_marks', args=[self.exam.id]), {
            f'theory_{self.student.id}': 40,
            f'practical_{self.student.id}': 20,
        })

        self.assertEqual(response.status_code, 403)
        self.assertFalse(Marks.objects.exists())

    def test_assigned_teacher_can_upload_marks(self):
        self.client.force_login(self.teacher_user)
        response = self.client.post(reverse('upload_marks', args=[self.exam.id]), {
            f'theory_{self.student.id}': 40,
            f'practical_{self.student.id}': 20,
        })

        self.assertRedirects(response, reverse('exam_list'))
        mark = Marks.objects.get(student=self.student, exam=self.exam)
        self.assertEqual(mark.total_marks, 60)
