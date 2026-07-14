from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from notices.models import Notice
from .models import AuditLog


class AuditLogsAppTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(username='admin_test', email='admin@test.com', password='password', role='admin')
        self.student_user = User.objects.create_user(username='student_test', email='student@test.com', password='password', role='student')
        
    def test_audit_logs_page_requires_login(self):
        response = self.client.get(reverse('audit_logs_list'))
        self.assertEqual(response.status_code, 302)

    def test_audit_logs_page_restricted_to_admin(self):
        self.client.login(username='student_test', password='password')
        response = self.client.get(reverse('audit_logs_list'))
        self.assertEqual(response.status_code, 403)

    def test_saving_model_records_audit_log(self):
        self.client.login(username='admin_test', password='password')
        
        # Create notice inside client session to trigger middleware request capture
        response = self.client.post(reverse('notice_create'), {
            'title': 'System Shutdown Notice',
            'content': 'Maintenance scheduled for tonight.',
            'priority': 'high',
            'is_active': True
        })
        self.assertEqual(response.status_code, 302)
        
        # Verify database record
        log = AuditLog.objects.filter(model_name='Notice').first()
        self.assertIsNotNone(log)
        self.assertEqual(log.user, self.admin)
        self.assertIn('System Shutdown Notice', log.details)
