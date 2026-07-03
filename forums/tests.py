from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from departments.models import Department
from courses.models import Course
from subjects.models import Subject
from students.models import Student
from teachers.models import Teacher
from forums.models import ForumThread, ForumPost
from datetime import date


class ForumsTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create users
        self.admin_user = User.objects.create_superuser(username='admin_test', email='admin@test.com', password='password123', role='admin')
        self.teacher_user = User.objects.create_user(username='teacher_test', email='teacher@test.com', password='password123', role='teacher')
        self.student_user = User.objects.create_user(username='student_test', email='student@test.com', password='password123', role='student')
        
        # Create academic hierarchies
        self.dept = Department.objects.create(name='CSE', code='CS')
        self.course = Course.objects.create(name='B.Tech', code='BT', department=self.dept, semester=8, credits=4)
        
        self.teacher = Teacher.objects.create(user=self.teacher_user, employee_id='EMP999', department=self.dept, qualification='Ph.D')
        self.student = Student.objects.create(user=self.student_user, admission_number='ADM999', roll_number='R999', gender='male', date_of_birth=date(2002, 1, 1), department=self.dept, course=self.course, semester=1, batch='2023')
        
        self.subject = Subject.objects.create(name='Mathematics', code='MA101', course=self.course, teacher=self.teacher, credits=4)
        
        # Create Thread
        self.thread = ForumThread.objects.create(subject=self.subject, author=self.admin_user, title='First Topic', content='Welcome to the board')

    def test_model_representations(self):
        self.assertEqual(str(self.thread), f"First Topic - {self.subject.name}")
        post = ForumPost.objects.create(thread=self.thread, author=self.student_user, content='Understood')
        self.assertEqual(str(post), f"Post by {self.student_user.username} on {self.thread.title}")

    def test_unauthorized_redirect(self):
        response = self.client.get(reverse('forum_list'))
        self.assertEqual(response.status_code, 302)

    def test_admin_forum_access(self):
        self.client.login(username='admin_test', password='password123')
        response = self.client.get(reverse('forum_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Available Discussion Boards')

    def test_student_forum_access_limits(self):
        # Student should only see subjects linked to their course
        self.client.login(username='student_test', password='password123')
        response = self.client.get(reverse('forum_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.subject.name)

    def test_create_thread_view(self):
        self.client.login(username='teacher_test', password='password123')
        response = self.client.post(reverse('create_thread', args=[self.subject.pk]), {
            'title': 'New Class Project',
            'content': 'Please submit ideas'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ForumThread.objects.filter(title='New Class Project').exists())

    def test_ajax_posts_list_polling(self):
        self.client.login(username='student_test', password='password123')
        # Create a reply post
        ForumPost.objects.create(thread=self.thread, author=self.teacher_user, content='Hello Class')
        
        # Normal GET request loads full page
        response = self.client.get(reverse('thread_detail', args=[self.thread.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Back to Thread List')
        
        # AJAX request loads only posts partial
        response = self.client.get(reverse('thread_detail', args=[self.thread.pk]), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Back to Thread List')
        self.assertContains(response, 'Hello Class')
