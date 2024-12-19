from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from .models import SellerRequest
from users.models import CustomUser

class SellerRequestTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = CustomUser.objects.create_user(
            email='admin@example.com',
            username='admin',
            password='password',
            role='admin'
        )
        self.regular_user = CustomUser.objects.create_user(
            email='user@example.com',
            username='user',
            password='password'
        )
        self.seller_request = SellerRequest.objects.create(user=self.regular_user)

    def test_admin_can_approve_seller_request(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(f'/api/seller-requests/{self.seller_request.id}/', {'status': 'approved'})
        
        self.regular_user.refresh_from_db()  # Memastikan untuk memperbarui instance pengguna
        self.assertEqual(response.status_code, status.HTTP_200_OK, 
                         f"Expected status code 200 OK, but got {response.status_code}.")
        self.assertTrue(self.regular_user.is_seller, 
                        f"Expected user {self.regular_user.email} to be a seller, but they are not.")
        print(f"Admin {self.admin_user.email} successfully approved seller request for {self.regular_user.email}.")

    def test_user_cannot_access_other_requests(self):
        self.client.force_authenticate(user=self.regular_user)

        # Coba akses permohonan orang lain
        response = self.client.get(f'/api/seller-requests/{self.seller_request.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, 
                         f"Expected status code 403 Forbidden, but got {response.status_code}.")
        print(f"User {self.regular_user.email} attempted to access another user's seller request and received {response.status_code} Forbidden.")

    def test_admin_can_reject_seller_request(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(f'/api/seller-requests/{self.seller_request.id}/', {'status': 'rejected'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK, 
                         f"Expected status code 200 OK, but got {response.status_code}.")
        self.seller_request.refresh_from_db()  # Memastikan status diperbarui dari database
        self.assertEqual(self.seller_request.status, 'rejected', 
                         f"Expected seller request status to be 'rejected', but got '{self.seller_request.status}'.")
        print(f"Admin {self.admin_user.email} successfully rejected seller request for {self.regular_user.email}.")

    def test_admin_can_update_seller_request(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(f'/api/seller-requests/{self.seller_request.id}/', {'status': 'approved'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK, 
                         f"Expected status code 200 OK, but got {response.status_code}.")
        self.seller_request.refresh_from_db()  # Pastikan instance diperbarui dari database
        self.assertEqual(self.seller_request.status, 'approved', 
                         f"Expected seller request status to be 'approved', but got '{self.seller_request.status}'.")
        print(f"Admin {self.admin_user.email} successfully updated seller request to approved.")
