from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from .models import Shop, Category, Product, Discount, Inventory

User = get_user_model()

class ShopViewSetTests(APITestCase):

    def setUp(self):
        """Setup users and admin for testing."""
        self.user = User.objects.create_user(
            email='testuser@example.com',
            username='testuser',
            password='testpassword123'
        )
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            username='admin',
            password='adminpassword'
        )
        self.user_token = AccessToken.for_user(self.user)
        self.admin_token = AccessToken.for_user(self.admin_user)
        self.shop_url = reverse('shop-list')  # URL for listing shops
        self.category = Category.objects.create(name="Electronics")  # Create a sample category

    def test_create_shop_as_owner(self):
        """Test owner creating a shop."""
        response = self.client.post(
            self.shop_url,
            {'shop_name': 'Owner Shop', 'description': 'Shop owned by the user.'},
            HTTP_AUTHORIZATION=f'Bearer {self.user_token}'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_shop_as_non_owner(self):
        """Test that a non-owner cannot create a shop."""
        self.client.logout()
        other_user = User.objects.create_user(
            email='otheruser@example.com',
            username='otheruser',
            password='otherpassword'
        )
        other_user_token = AccessToken.for_user(other_user)
        response = self.client.post(
            self.shop_url,
            {'shop_name': 'Non-owner Shop', 'description': 'Shop not owned by this user.'},
            HTTP_AUTHORIZATION=f'Bearer {other_user_token}'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_update_shop(self):
        """Test that owner can update their own shop."""
        response = self.client.post(
            self.shop_url,
            {'shop_name': 'Shop to Update', 'description': 'Original description.'},
            HTTP_AUTHORIZATION=f'Bearer {self.user_token}'
        )
        shop_id = response.data['id']
        update_response = self.client.put(
            reverse('shop-detail', args=[shop_id]),
            {'shop_name': 'Updated Shop Name', 'description': 'Updated description.'},
            HTTP_AUTHORIZATION=f'Bearer {self.user_token}'
        )
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)

    def test_user_cannot_update_other_shop(self):
        """Test that user cannot update a shop they don't own."""
        response = self.client.post(
            self.shop_url,
            {'shop_name': 'Shop for Admin', 'description': 'Admin owned shop.'},
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token}'
        )
        shop_id = response.data['id']
        self.client.logout()
        other_user_token = AccessToken.for_user(self.user)
        response = self.client.put(
            reverse('shop-detail', args=[shop_id]),
            {'shop_name': 'Attempted Update', 'description': 'User cannot update this.'},
            HTTP_AUTHORIZATION=f'Bearer {other_user_token}'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
