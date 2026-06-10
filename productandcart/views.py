from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from .models import Category, Product, CartItem, Cart, Order, OrderItem
from drf_spectacular.utils import extend_schema
from .serializers import (
    CategorySerializer, ProductSerializer, CartItemSerializer, CartSerializer, 
    CartRequestSerializer, OrderSerializer, CreateOrderSerializer, OrderItemSerializer
)


# Helper Functions
def get_product_or_error(product_id):
    """Get product by ID or return error response"""
    try:
        return Product.objects.get(id=product_id), None
    except Product.DoesNotExist:
        return None, Response(
            {"error": "Product not found"},
            status=status.HTTP_404_NOT_FOUND
        )


def get_or_create_cart(user=None):
    """Get or create user's cart"""
    if user and user.is_authenticated:
        return Cart.objects.get_or_create(user=user)[0]
    else:
        # For anonymous users, create a session-based cart
        return Cart.objects.get_or_create(user=None)[0]


# Product Views
class ProductList(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class CategoryList(APIView):
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)


class ProductDetail(APIView):
    def get(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
            serializer = ProductSerializer(product)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)


# Cart Views
class CartDetail(APIView):
    def get(self, request):
        cart = get_or_create_cart(request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @extend_schema(
        request=CartRequestSerializer,
        responses={200: None}
    )
    def post(self, request):
        serializer = CartRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data['product_id']
        product, error = get_product_or_error(product_id)
        
        if error:
            return error

        cart = get_or_create_cart(request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not created:
            cart_item.quantity += 1
            cart_item.save()

        return Response(
            {"message": "Product added to cart"},
            status=status.HTTP_200_OK
        )


class RemoveFromCart(APIView):
    @extend_schema(
        request=CartRequestSerializer,
        responses={200: None}
    )
    def post(self, request):
        serializer = CartRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data['product_id']
        product, error = get_product_or_error(product_id)
        
        if error:
            return error

        cart = get_or_create_cart(request.user)

        try:
            cart_item = CartItem.objects.get(
                cart=cart,
                product=product
            )

            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()

            return Response(
                {"message": "Product removed from cart"},
                status=status.HTTP_200_OK
            )

        except CartItem.DoesNotExist:
            return Response(
                {"error": "Product not in cart"},
                status=status.HTTP_404_NOT_FOUND
            )
        
class CreateOrder(APIView):
    @extend_schema(
        request=CreateOrderSerializer,
        responses={201: OrderSerializer}
    )
    def post(self, request):
        try:
            serializer = CreateOrderSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            cart = get_or_create_cart(request.user)
            
            if not cart or not cart.items.exists():
                return Response(
                    {'error': 'Cart is empty'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Calculate total price
            total = sum(item.product.price * item.quantity for item in cart.items.all())

            # Create order
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                total_price=total
            )

            # Create order items from cart items
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )

            # Clear the cart
            cart.items.all().delete()

            order_serializer = OrderSerializer(order)
            return Response(
                {
                    "message": "Order created successfully",
                    "order": order_serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class OrderList(APIView):
    """Get all orders for authenticated user"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if request.user.is_authenticated:
            orders = Order.objects.filter(user=request.user).order_by('-created_at')
        else:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


class OrderDetail(APIView):
    """Get details of a specific order"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
            
            # Check if user owns this order
            if order.user != request.user and not request.user.is_staff:
                return Response(
                    {'error': 'You do not have permission to view this order'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            serializer = OrderSerializer(order)
            return Response(serializer.data)
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )