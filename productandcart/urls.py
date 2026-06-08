from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.ProductList.as_view(), name='product-list'),
    path('categories/', views.CategoryList.as_view(), name='category-list'),
]
