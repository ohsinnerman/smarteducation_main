from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class DashboardRoleFallbackTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='no_profile_user', password='testpass123')

    def test_admin_dashboard_handles_user_without_profile(self):
        self.client.force_login(self.user)
        response = self.client.get('/dashboards/admin/')
        self.assertEqual(response.status_code, 302)

    def test_parent_portal_url_alias_redirects(self):
        response = self.client.get('/advanced_features/parent_portal/')
        self.assertIn(response.status_code, [301, 302])

    def test_dashboard_report_download_url_is_available(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('dashboards:dashboard_report_download'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('Smart Education', response.content.decode())
