from django.test import TestCase
from django.urls import reverse
from accounts.models import User
from departments.models import Department
from .models import Course

class CourseTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin1', password='password', role='admin')
        self.dept = Department.objects.create(name='Computer Science', code='CS101')
        self.course = Course.objects.create(name='B.Tech CS', code='BTCS', department=self.dept, semester=8)

    def test_course_creation(self):
        self.assertEqual(str(self.course), 'B.Tech CS (BTCS)')
        
    def test_course_list_admin(self):
        self.client.login(username='admin1', password='password')
        response = self.client.get(reverse('course_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'B.Tech CS')

    def test_course_create_admin(self):
        self.client.login(username='admin1', password='password')
        response = self.client.post(reverse('course_create'), {
            'name': 'M.Tech CS', 'code': 'MTCS', 'department': self.dept.id, 'semester': 4,
            'credits': 4, 'is_active': True
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Course.objects.filter(code='MTCS').exists())
