from rest_framework import serializers
from .models import Cart, Order, Shipping
from shops.models import Product


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'user', 'product', 'quantity', 'total_price']
        read_only_fields = ['user', 'total_price']


class OrderSerializer(serializers.ModelSerializer):
    cart_items = CartSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'cart_items', 'total_price', 'borrow_date', 'return_deadline', 'status', 'created_at', 'updated_at']
        read_only_fields = ['user', 'status', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Mendapatkan user dari request (dari context)
        user = self.context['request'].user  # Mendapatkan user yang sedang login

        # Mengambil data cart_items
        cart_items = validated_data.get('cart_items', [])
        
        # Menghitung total price dari semua cart_items
        total_price = sum(item.product.price * item.quantity for item in cart_items)

        # Membuat order baru dengan total_price yang dihitung
        order = Order.objects.create(
            user=user,  # Menetapkan user yang sedang login
            total_price=total_price,
            **validated_data
        )
        
        # Menambahkan cart items ke dalam order
        order.cart_items.set(cart_items)
        order.save()
        
        return order




class ShippingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipping
        fields = ['id', 'order', 'address', 'postal_code', 'phone_number', 'user_name']
