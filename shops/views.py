# views.py

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Shop
from .serializers import ShopSerializer
from .models import Product, Category, Discount, Inventory
from .serializers import ProductSerializer, CategorySerializer, DiscountSerializer, InventorySerializer
from .permissions import IsOwnerOrReadOnly

class ShopViewSet(viewsets.ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        # Menetapkan pengguna saat ini sebagai pemilik toko
        serializer.save(user=self.request.user)
    
    def get_queryset(self):
        # Filter toko yang dimiliki oleh user saat ini
        return Shop.objects.filter(user=self.request.user)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        # Batasi produk hanya untuk toko milik pengguna saat ini
        return Product.objects.filter(shop__user=self.request.user)

    def perform_create(self, serializer):
        # Ambil toko pengguna saat ini
        shop = Shop.objects.filter(user=self.request.user).first()
        if not shop:
            raise PermissionError("You do not have a shop to add products to.")
        
        # Simpan produk dengan toko pengguna saat ini
        serializer.save(shop=shop)



class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]  # Tambahkan jika hanya pengguna tertentu yang boleh akses


class DiscountViewSet(viewsets.ModelViewSet):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

