from django.contrib.auth.models import Group
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets
from .models import Category, MenuItem, Cart, Order
from .serializers import CategorySerializer, MenuItemSerializer, CartSerializer, OrderSerializer
from rest_framework.pagination import PageNumberPagination

class MenuItemPagination(PageNumberPagination):
    page_size = 2
    page_size_query_param = 'page_size'
    max_page_size = 1000

class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = MenuItemPagination  # Add this line


# Manager-only access
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def manager_view(request):
    if request.user.groups.filter(name="Manager").exists():
        return Response({"message": "Only Manager should see this."})
    return Response({"error": "You are not authorized to view this."}, status=403)

# ViewSet for categories (open to all authenticated users)
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

# ViewSet for menu items (only Managers can modify)
class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="Manager").exists():
            return Response({"error": "Only Managers can add menu items."}, status=403)
        return super().create(request, *args, **kwargs)

# ViewSet for Cart (Only Customers can add items)
class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="Customer").exists():
            return Response({"error": "Only Customers can add items to cart."}, status=403)
        return super().create(request, *args, **kwargs)

# ViewSet for Orders (Only Delivery Crew can update)
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="Delivery Crew").exists():
            return Response({"error": "Only Delivery Crew can update orders."}, status=403)
        return super().update(request, *args, **kwargs)
