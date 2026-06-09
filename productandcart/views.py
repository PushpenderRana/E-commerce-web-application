from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Category, Product, CartItem, Cart
from drf_spectacular.utils import extend_schema
from .serializers import CategorySerializer, ProductSerializer, CartItemSerializer, CartSerializer, CartRequestSerializer


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


def get_or_create_cart():
    """Get or create user's cart"""
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
        cart = get_or_create_cart()
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

        cart = get_or_create_cart()
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

        cart = get_or_create_cart()

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