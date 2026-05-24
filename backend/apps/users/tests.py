from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken


User = get_user_model()


class ChangePasswordSecurityTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='reader',
            email='reader@example.com',
            password='OldPass123!',
        )

    def test_change_password_blacklists_existing_refresh_tokens(self):
        login_response = self.client.post(
            '/api/users/auth/login/',
            {'username': 'reader', 'password': 'OldPass123!'},
            format='json',
        )
        tokens = login_response.data['tokens']

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
        response = self.client.post(
            '/api/users/change-password/',
            {'current_password': 'OldPass123!', 'new_password': 'NewPass123!'},
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['reauthenticate'])
        self.assertEqual(
            BlacklistedToken.objects.filter(token__user=self.user).count(),
            OutstandingToken.objects.filter(user=self.user).count(),
        )

        refresh_response = self.client.post(
            '/api/users/auth/token/refresh/',
            {'refresh': tokens['refresh']},
            format='json',
        )
        self.assertEqual(refresh_response.status_code, 401)

    def test_change_password_uses_django_password_validation(self):
        login_response = self.client.post(
            '/api/users/auth/login/',
            {'username': 'reader', 'password': 'OldPass123!'},
            format='json',
        )
        tokens = login_response.data['tokens']

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
        response = self.client.post(
            '/api/users/change-password/',
            {'current_password': 'OldPass123!', 'new_password': '123'},
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('new_password', response.data)
