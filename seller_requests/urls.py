# seller_requests/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SellerRequestViewSet

router = DefaultRouter()
router.register(r'seller-requests', SellerRequestViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
