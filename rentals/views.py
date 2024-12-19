from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Cart, Order, Shipping
from .serializers import CartSerializer, OrderSerializer, ShippingSerializer
from .permissions import IsOrderOwnerOrReadOnly, IsOwnerOrReadOnly


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def checkout(self, request):
        user_cart = Cart.objects.filter(user=request.user)
        if not user_cart.exists():
            return Response({"detail": "Cart is empty"}, status=400)

        total_price = sum(item.product.price * item.quantity for item in user_cart)
        order = Order.objects.create(
            user=request.user,
            total_price=total_price,
            borrow_date=request.data.get('borrow_date'),
            return_deadline=request.data.get('return_deadline'),
        )
        order.cart_items.set(user_cart)
        user_cart.delete()
        return Response({"detail": "Order created", "order_id": order.id}, status=201)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsOrderOwnerOrReadOnly]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)
    
    def post(self, request, *args, **kwargs):
        # Menetapkan user ke dalam data serializer
        data = request.data
        data['user'] = request.user.id  # Menetapkan user yang sedang login

        serializer = OrderSerializer(data=data)
        if serializer.is_valid():
            order = serializer.save()  # Menyimpan order
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def request_cancel(self, request, pk=None):
        order = self.get_object()
        if order.status != 'pending':
            return Response({"detail": "Cannot cancel order in current status"}, status=400)
        order.status = 'cancel_requested'
        order.save()
        return Response({"detail": "Cancel request submitted"}, status=200)

    @action(detail=True, methods=['post'])
    def confirm_received(self, request, pk=None):
        order = self.get_object()
        if order.status != 'shipping':
            return Response({"detail": "Order is not in shipping status"}, status=400)
        order.status = 'borrowed'
        order.save()
        return Response({"detail": "Order confirmed as borrowed"}, status=200)


class ShippingViewSet(viewsets.ModelViewSet):
    queryset = Shipping.objects.all()
    serializer_class = ShippingSerializer
    permission_classes = [IsAuthenticated, IsOrderOwnerOrReadOnly]
