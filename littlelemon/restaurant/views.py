from django.contrib.auth.models import Group, User
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework.response import Response
from rest_framework import viewsets, status, filters
from rest_framework.throttling import UserRateThrottle
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, MenuItem, Cart, Order
from .serializers import CategorySerializer, MenuItemSerializer, CartSerializer, OrderSerializer
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.authentication import JWTAuthentication


#Project done by Aayush Sapkota


# Custom Throttle Classes
class BurstRateThrottle(UserRateThrottle):
    scope = 'burst'


class SustainedRateThrottle(UserRateThrottle):
    scope = 'sustained'


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
    authentication_classes = [JWTAuthentication]
    throttle_classes = [BurstRateThrottle, SustainedRateThrottle]  # Apply throttling


# ViewSet for menu items (only Managers can modify)
class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated]

    # Add filtering/searching/sorting backends
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Filtering fields
    filterset_fields = ['category', 'featured', 'price']
    
    # Searching fields (must match model fields or related fields)
    search_fields = ['title', 'category__title']
    
    # Ordering fields
    ordering_fields = ['price', 'title']

    # Apply throttling classes
    throttle_classes = [BurstRateThrottle, SustainedRateThrottle]

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
    
    def partial_update(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="Manager").exists():
            return Response({"error": "Only Managers can update menu items."}, status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)


# ViewSet for Cart (Only Customers can add items)
class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    
    # Apply throttling classes
    throttle_classes = [BurstRateThrottle]

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
    
    # Apply throttling classes
    throttle_classes = [BurstRateThrottle]

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
        order = self.get_object()

        # Only Delivery Crew can update the status
        if request.user.groups.filter(name="Delivery Crew").exists():
            # Delivery crew can only update the status
            serializer = self.get_serializer(order, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        # Only Managers can assign a delivery crew
        elif request.user.groups.filter(name="Manager").exists():
            # Managers can only assign delivery crew
             serializer = self.get_serializer(order, data=request.data, partial=True)
             serializer.is_valid(raise_exception=True)
             serializer.save()
             return Response(serializer.data)
        else:
            return Response({"error": "You are not authorized to update orders."}, status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="Manager").exists():
            return Response({"error": "Only Managers can delete orders."}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404

class UserViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def assign_to_delivery_crew(self, request, pk=None):
        if not request.user.groups.filter(name="Manager").exists():
            return Response({"error": "Only Managers can assign users to delivery crew."}, status=status.HTTP_403_FORBIDDEN)
        user = get_object_or_404(User, pk=pk)
        delivery_crew_group = Group.objects.get(name="Delivery Crew")
        user.groups.add(delivery_crew_group)
        return Response({"message": f"User {user.username} assigned to Delivery Crew."}, status=status.HTTP_200_OK)
