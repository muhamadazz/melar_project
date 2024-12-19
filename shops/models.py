from django.db import models
from django.conf import settings
from django.utils import timezone

class Shop(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='shops',
        on_delete=models.CASCADE,
        verbose_name='Pemilik Toko'
    )
    shop_name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)  # Deskripsi toko
    is_active = models.BooleanField(default=True)  # Status aktif/inaktif
    address = models.CharField(max_length=255)  # Alamat toko
    postal_code = models.CharField(max_length=10)  # Kode pos toko
    contact = models.CharField(max_length=20)  # Kontak toko, bisa berupa nomor telepon
    created_at = models.DateTimeField(default=timezone.now)  # Waktu pembuatan
    updated_at = models.DateTimeField(auto_now=True)  # Waktu pembaruan

    def __str__(self):
        return self.shop_name

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    AVAILABILITY_CHOICES = [
        ('available', 'Available'),
        ('rented', 'Rented'),
        ('unavailable', 'Unavailable'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('blocked', 'Blocked'),
    ]

    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    availability_status = models.CharField(max_length=20, choices=AVAILABILITY_CHOICES, default='available')
    categories = models.ManyToManyField(Category, related_name='products', blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Discount(models.Model):
    code = models.CharField(max_length=50, unique=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    valid_from = models.DateField()
    valid_until = models.DateField()
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='discounts')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='discounts')
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_discounts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code

class Inventory(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='inventory')
    quantity = models.PositiveIntegerField(default=0)  # Jumlah harus tidak negatif
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} - {self.quantity} items"
