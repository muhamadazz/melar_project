from django.urls import path, include
from rest_framework.routers import DefaultRouter # type: ignore
from . import views

router = DefaultRouter()
router.register(r'shops', views.ShopViewSet)  # 'shops' adalah bagian dari URL
router.register(r'products', views.ProductViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'discounts', views.DiscountViewSet)
router.register(r'inventory', views.InventoryViewSet)

urlpatterns = [
    path('', include(router.urls)),  # URL dasar untuk mengakses router
]