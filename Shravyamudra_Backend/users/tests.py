from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()

class AuthLoggingTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')

    def test_login_logging(self):
        # Test successful login
        response = self.client.post('/api/auth/login/', {'username': 'testuser', 'password': 'testpassword'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Test failed login (wrong password)
        response = self.client.post('/api/auth/login/', {'username': 'testuser', 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test failed login (non-existent user)
        response = self.client.post('/api/auth/login/', {'username': 'nonexistent', 'password': 'password'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
