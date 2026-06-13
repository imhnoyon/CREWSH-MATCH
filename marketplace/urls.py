from django.urls import path
from .views import ProductCreateAPIView, ProductDetailAPIView, ProductChatAPIView

urlpatterns = [
    path('products/create/', ProductCreateAPIView.as_view(), name='product-create'),
    path('products/details/<int:pk>/', ProductDetailAPIView.as_view(), name='product-detail'),
    path('products/<int:pk>/chat/', ProductChatAPIView.as_view(), name='product-chat'),
]
