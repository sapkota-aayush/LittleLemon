from rest_framework import serializers
from .models import Category, MenuItem, Cart, Order, OrderItem

# Category Serializer
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'  # Includes all fields

# MenuItem Serializer
class MenuItemSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()  # Displays category name instead of ID

    class Meta:
        model = MenuItem
        fields = '__all__'

# Cart Serializer
class CartSerializer(serializers.ModelSerializer):
    menu_item = serializers.StringRelatedField()  # Displays menu item name

    class Meta:
        model = Cart
        fields = '__all__'

# OrderItem Serializer
class OrderItemSerializer(serializers.ModelSerializer):
    menu_item = serializers.StringRelatedField()  # Displays menu item name

    class Meta:
        model = OrderItem
        fields = '__all__'

# Order Serializer
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)  # Nested serializer

    class Meta:
        model = Order
        fields = '__all__'
