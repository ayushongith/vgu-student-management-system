from django.test import TestCase

from accounts.models import User
from courses.models import Course
from departments.models import Department
from students.forms import StudentForm
from students.models import Student


class StudentFormTests(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name='Computer Science', code='CS')
        self.course = Course.objects.create(
            name='MCA', code='MCA', department=self.department, semester=1
        )

    def form_data(self, **overrides):
        data = {
            'first_name': 'Deepak',
            'last_name': 'Sharma',
            'email': 'deepak@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'admission_number': 'A001',
            'roll_number': 'R001',
            'gender': 'male',
            'date_of_birth': '2000-01-01',
            'blood_group': 'O+',
            'phone': '8888888888',
            'parent_name': 'Parent',
            'parent_contact': '7777777777',
            'address': 'Address',
            'department': self.department.id,
            'course': self.course.id,
            'semester': 1,
            'batch': '2026',
        }
        data.update(overrides)
        return data

    def test_create_student_uses_submitted_password(self):
        form = StudentForm(data=self.form_data())

        self.assertTrue(form.is_valid(), form.errors)
        student = form.save()

        self.assertTrue(student.user.check_password('StrongPass123!'))
        self.assertFalse(student.user.check_password('student123'))
        self.assertEqual(student.user.role, 'student')

    def test_update_student_updates_linked_user(self):
        user = User.objects.create_user(
            username='student', password='OldPass123!', role='student'
        )
        student = Student.objects.create(
            user=user,
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

        form = StudentForm(
            data=self.form_data(
                first_name='Updated',
                email='updated@example.com',
                password1='',
                password2='',
            ),
            instance=student,
        )

        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        user.refresh_from_db()

        self.assertEqual(user.first_name, 'Updated')
        self.assertEqual(user.email, 'updated@example.com')
        self.assertTrue(user.check_password('OldPass123!'))
