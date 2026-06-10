from rest_framework import serializers
from .models import CartItem, Category, Product, Cart, Order, OrderItem

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    class Meta:
        model = Product
        fields = ['id', 'category', 'name', 'description', 'price', 'image']

class CartRequestSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    product_quantity = serializers.IntegerField(default=1)
    product_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    

class CartItemSerializer(serializers.ModelSerializer):
    product = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    product_image = serializers.ImageField(source='product.image', read_only=True)
    class Meta:
        model = CartItem
        fields = "__all__"

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = "__all__"

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.ImageField(source='product.image', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_image', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'user', 'created_at', 'total_price', 'items']

class CreateOrderSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100, required=False)
    email = serializers.EmailField(required=False)
    address = serializers.CharField(max_length=255, required=False)
    phone = serializers.CharField(max_length=20, required=False)
    payment_method = serializers.CharField(max_length=50, default='COD')