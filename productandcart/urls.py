from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.ProductList.as_view(), name='product-list'),
    path('products/<int:pk>/', views.ProductDetail.as_view(), name='product-detail'),
    path('categories/', views.CategoryList.as_view(), name='category-list'),
    path('cart/', views.CartDetail.as_view(), name='cart-detail'),
    path('cart/remove/', views.RemoveFromCart.as_view(), name='remove-from-cart'),
    path('order/create/', views.CreateOrder.as_view(), name='create-order'),
    path('orders/', views.OrderList.as_view(), name='order-list'),
    path('orders/<int:pk>/', views.OrderDetail.as_view(), name='order-detail'),
]
