from rest_framework import serializers
from .models import Shop, Category, Product, Discount, Inventory

class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['id', 'user', 'shop_name', 'description', 'is_active','address', 'postal_code', 'contact',  'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']

class CategorySerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()  # Tambahkan daftar produk terkait

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'products', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def get_products(self, obj):
        # Ambil produk yang terkait dengan kategori ini
        products = obj.products.all()  # Field related_name='products' pada ManyToManyField
        return ProductSerializer(products, many=True).data  # Serialize data produk terkait



class ProductSerializer(serializers.ModelSerializer):
    categories = serializers.ListField(
        child=serializers.CharField(), write_only=True
    )  # Input kategori sebagai list nama
    shop = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'availability_status',
            'categories', 'shop', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        category_names = validated_data.pop('categories', [])
        shop = validated_data.pop('shop')
        # Buat atau ambil kategori berdasarkan nama
        categories = []
        for name in category_names:
            category, created = Category.objects.get_or_create(name=name)
            categories.append(category)
        # Buat produk
        product = Product.objects.create(shop=shop, **validated_data)
        product.categories.set(categories)  # Tetapkan kategori ke produk
        return product




class DiscountSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)  # Menampilkan informasi produk terkait diskon
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )  # Untuk input ID produk
    category = CategorySerializer(read_only=True)  # Menampilkan kategori terkait diskon
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )  # Untuk input ID kategori
    admin = serializers.StringRelatedField()  # Menampilkan nama admin

    class Meta:
        model = Discount
        fields = [
            'id', 'code', 'percentage', 'valid_from', 'valid_until', 
            'product', 'product_id', 'category', 'category_id', 'admin', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class InventorySerializer(serializers.ModelSerializer): 
    product = ProductSerializer(read_only=True)  # Menampilkan informasi produk terkait inventaris
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )  # Untuk input ID produk

    class Meta:
        model = Inventory
        fields = ['id', 'product', 'product_id', 'quantity', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
