from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class UserTests(APITestCase):
    
    def setUp(self):
        """Setup before each test."""
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.change_password_url = reverse('change_password')
        self.profile_url = reverse('profile')

        self.user_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'full_name': 'Test User',
            'password': 'testpassword123'
        }
        self.user = User.objects.create_user(**self.user_data)
        self.user.is_active = True
        self.user.save()
        
        self.client.force_authenticate(user=self.user)  # Authenticate the user for subsequent tests

    def test_register_user(self):
        """Test user registration."""
        response = self.client.post(self.register_url, {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'full_name': 'New User',
            'password': 'newpassword123'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)

    def test_login_user(self):
        """Test user login."""
        response = self.client.post(self.login_url, {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)

    def test_logout_user(self):
        """Test user logout."""
        # Logout without sending an invalid refresh token
        response = self.client.post(self.logout_url, {'refresh': 'dummy_refresh_token'})  
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  # Expecting an error because the token is invalid

        # Test logging out a valid user
        self.client.logout()  # Use Django's built-in logout for APIClient

    def test_change_password(self):
        """Test changing the user password."""
        response = self.client.post(self.change_password_url, {
            'old_password': 'testpassword123',
            'new_password': 'newpassword456',
            'confirm_new_password': 'newpassword456'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()  # Refresh to get the latest user data
        self.assertTrue(self.user.check_password('newpassword456'))  # Check if the new password is set correctly

    def test_update_profile(self):
        """Test updating user profile."""
        response = self.client.patch(self.profile_url, {
            'full_name': 'Updated User Name',
            'role': 'user'  # Assuming the user is allowed to change their own role
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()  # Refresh to get the latest user data
        self.assertEqual(self.user.full_name, 'Updated User Name')

    def test_access_profile_without_authentication(self):
        """Test access to profile without authentication."""
        self.client.logout()  # Logout to test unauthenticated access
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
