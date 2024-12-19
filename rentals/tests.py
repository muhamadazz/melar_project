from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from shops.models import Product, Shop
from .models import Cart, Order, Shipping

User = get_user_model() 

class CartOrderShippingTests(APITestCase):

    def setUp(self):
        # Create user and authenticate
        self.user = User.objects.create_user(username='testuser',email='testuser@gmail.com', password='password123')
        self.client.login(username='testuser@gmail.com', password='password123')

        # Create another user for testing
        self.other_user = User.objects.create_user(email='testuser2@gmail.com',username='otheruser', password='password123')

        # Create shop and product
        self.shop = Shop.objects.create(user=self.user, shop_name="Test Shop", address="Test Address", postal_code="12345", contact="123456789")
        self.product = Product.objects.create(
            shop=self.shop,
            name="Test Product",
            description="Description of test product",
            price=100.00,
            availability_status="available"
        )

        # URLs
        self.cart_url = reverse('cart-list')
        self.order_url = reverse('order-list')
        self.shipping_url = reverse('shipping-list')

    ### CART TESTS ###
    def test_add_product_to_cart(self):
        payload = {
            "product": self.product.id,
            "quantity": 2
        }
        response = self.client.post(self.cart_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Cart.objects.count(), 1)
        cart = Cart.objects.first()
        self.assertEqual(cart.product, self.product)
        self.assertEqual(cart.quantity, 2)

    def test_view_cart_items(self):
        Cart.objects.create(user=self.user, product=self.product, quantity=1)
        response = self.client.get(self.cart_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_update_cart_item_quantity(self):
        cart = Cart.objects.create(user=self.user, product=self.product, quantity=1)
        url = reverse('cart-detail', args=[cart.id])
        payload = {"quantity": 5}
        response = self.client.patch(url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cart.refresh_from_db()
        self.assertEqual(cart.quantity, 5)

    def test_delete_cart_item(self):
        cart = Cart.objects.create(user=self.user, product=self.product, quantity=1)
        url = reverse('cart-detail', args=[cart.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Cart.objects.count(), 0)

    def test_checkout_creates_order(self):
        Cart.objects.create(user=self.user, product=self.product, quantity=2)
        payload = {
            "borrow_date": "2024-12-01",
            "return_deadline": "2024-12-10"
        }
        response = self.client.post(f"{self.cart_url}checkout/", payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(Cart.objects.count(), 0)

    ### ORDER TESTS ###
    def test_view_order_history(self):
        order = Order.objects.create(user=self.user, total_price=200.00, borrow_date="2024-12-01", return_deadline="2024-12-10")
        response = self.client.get(self.order_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_request_order_cancellation(self):
        order = Order.objects.create(user=self.user, total_price=200.00, borrow_date="2024-12-01", return_deadline="2024-12-10", status="pending")
        url = reverse('order-request-cancel', args=[order.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.status, "cancel_requested")

    def test_confirm_order_received(self):
        order = Order.objects.create(user=self.user, total_price=200.00, borrow_date="2024-12-01", return_deadline="2024-12-10", status="shipping")
        url = reverse('order-confirm-received', args=[order.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.status, "borrowed")

    ### SHIPPING TESTS ###
    def test_create_shipping_for_order(self):
        order = Order.objects.create(user=self.user, total_price=200.00, borrow_date="2024-12-01", return_deadline="2024-12-10", status="pending")
        payload = {
            "order": order.id,
            "address": "123 Main St",
            "postal_code": "12345",
            "phone_number": "1234567890",
            "user_name": "Test User"
        }
        response = self.client.post(self.shipping_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Shipping.objects.count(), 1)
        shipping = Shipping.objects.first()
        self.assertEqual(shipping.order, order)
        self.assertEqual(shipping.address, "123 Main St")
