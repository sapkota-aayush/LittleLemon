from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from restaurant.views import (
    CategoryViewSet, MenuItemViewSet, CartViewSet, OrderViewSet, manager_view
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'menu-items', MenuItemViewSet)
router.register(r'cart', CartViewSet)
router.register(r'orders', OrderViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    # Djoser endpoints for user management and token authentication:
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    # Your API endpoints:
    path('', include(router.urls)),
    path('manager-only/', manager_view, name="manager-view"),
]
