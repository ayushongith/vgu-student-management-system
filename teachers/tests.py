from django.test import TestCase

from accounts.models import User
from departments.models import Department
from teachers.forms import TeacherForm
from teachers.models import Teacher


class TeacherFormTests(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name='Computer Science', code='CS')

    def form_data(self, **overrides):
        data = {
            'first_name': 'Anita',
            'last_name': 'Rao',
            'email': 'anita@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'employee_id': 'T001',
            'department': self.department.id,
            'qualification': 'M.Tech',
            'phone': '9999999999',
            'address': 'Address',
        }
        data.update(overrides)
        return data

    def test_create_teacher_uses_submitted_password(self):
        form = TeacherForm(data=self.form_data())

        self.assertTrue(form.is_valid(), form.errors)
        teacher = form.save()

        self.assertTrue(teacher.user.check_password('StrongPass123!'))
        self.assertFalse(teacher.user.check_password('teacher123'))
        self.assertEqual(teacher.user.role, 'teacher')

    def test_update_teacher_updates_linked_user(self):
        user = User.objects.create_user(
            username='teacher', password='OldPass123!', role='teacher'
        )
        teacher = Teacher.objects.create(
            user=user,
            employee_id='T001',
            department=self.department,
            qualification='M.Tech',
            phone='9999999999',
            address='Address',
        )

        form = TeacherForm(
            data=self.form_data(
                first_name='Updated',
                email='updated@example.com',
                password1='',
                password2='',
            ),
            instance=teacher,
        )

        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        user.refresh_from_db()

        self.assertEqual(user.first_name, 'Updated')
        self.assertEqual(user.email, 'updated@example.com')
        self.assertTrue(user.check_password('OldPass123!'))
