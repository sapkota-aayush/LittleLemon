from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from restaurant.views import CategoryViewSet, MenuItemViewSet, CartViewSet, OrderViewSet
from restaurant.views import manager_view  # Import the new view


# Create a router & register our ViewSets
router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'menu-items', MenuItemViewSet)
router.register(r'cart', CartViewSet)
router.register(r'orders', OrderViewSet)

# Include router URLs
urlpatterns = [
    path('admin/', admin.site.urls),  # Ensure this line is included for the admin panel
    path('', include(router.urls)),  # This includes all API routes from the router
    path('manager-only/', manager_view),  # New route for manager-only access
]
