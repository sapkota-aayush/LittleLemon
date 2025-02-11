from django.contrib.auth.models import Group
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets, status, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, MenuItem, Cart, Order
from .serializers import CategorySerializer, MenuItemSerializer, CartSerializer, OrderSerializer


# Manager-only access
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def manager_view(request):
    if request.user.groups.filter(name="Manager").exists():
        return Response({"message": "Only Manager should see this."})
    return Response({"error": "You are not authorized to view this."}, status=status.HTTP_403_FORBIDDEN)


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

    # Add pagination and filtering/searching/sorting backends
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    # Filtering fields
    filterset_fields = ['category', 'featured', 'price']

    # Searching fields
    search_fields = ['title', 'category__title']

    # Ordering fields
    ordering_fields = ['price', 'title']

    def create(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="Manager").exists():
            return Response({"error": "Only Managers can add menu items."}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="Manager").exists():
            return Response({"error": "Only Managers can update menu items."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="Manager").exists():
            return Response({"error": "Only Managers can delete menu items."}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


# ViewSet for Cart (Only Customers can add items)
class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter cart items by the logged-in user
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Automatically associate the logged-in user with the cart item
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="Customer").exists():
            return Response({"error": "Only Customers can add items to cart."}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)


# ViewSet for Orders (Only Delivery Crew can update)
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Managers can see all orders
        if user.groups.filter(name="Manager").exists():
            return Order.objects.all()

        # Delivery Crew can see only their assigned orders
        elif user.groups.filter(name="Delivery Crew").exists():
            return Order.objects.filter(delivery_crew=user)

        # Customers can see only their own orders
        else:
            return Order.objects.filter(user=user)

    def perform_create(self, serializer):
        # Automatically associate the logged-in user with the order
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="Delivery Crew").exists():
            return Response({"error": "Only Delivery Crew can update orders."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="Manager").exists():
            return Response({"error": "Only Managers can delete orders."}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)
