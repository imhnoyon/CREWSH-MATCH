from django.urls import path
from .views import *
urlpatterns = [
    path('products/create/', ProductCreateAPIView.as_view(), name='product-create'),
    path('products/details/<int:pk>/', ProductDetailAPIView.as_view(), name='product-detail'),
]
