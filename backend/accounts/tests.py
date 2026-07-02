from django.contrib.auth import get_user_model
from django.test import TestCase


class DemoAccountSetupTests(TestCase):
    def test_demo_accounts_are_created_on_startup(self):
        user_model = get_user_model()
        self.assertTrue(user_model.objects.filter(username='admin_demo').exists())
        self.assertTrue(user_model.objects.filter(username='teacher_demo').exists())
        self.assertTrue(user_model.objects.filter(username='student_demo1').exists())
        self.assertTrue(user_model.objects.filter(username='parent_demo').exists())
