from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.ProductList.as_view(), name='product-list'),
    path('products/<int:pk>/', views.ProductDetail.as_view(), name='product-detail'),
    path('categories/', views.CategoryList.as_view(), name='category-list'),
    path('cart/', views.CartDetail.as_view(), name='cart-detail'),
    path('cart/remove/', views.RemoveFromCart.as_view(), name='remove-from-cart'),
]
