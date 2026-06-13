from datetime import timedelta
from django.db.models import Q
from rest_framework import status
from django.shortcuts import render
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Product
from marketplace.serializers import ProductSerializer
from match.models import Match

# Create your views here.
class ProductCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ProductSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            product = serializer.save(
                user=request.user,
                valid_until=timezone.now() + timedelta(days=7)
            )

            return Response(
                ProductSerializer(product).data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
        
    def get(self, request):
        Product.delete_expired()
        products = Product.objects.filter(valid_until__gt=timezone.now())
        serializer = ProductSerializer(products, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    
class ProductDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        Product.delete_expired()

        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductChatAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        Product.delete_expired()

        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        if product.user == request.user:
            return Response({'error': 'Cannot start chat with yourself'}, status=status.HTTP_400_BAD_REQUEST)

        seller = product.user
        match = Match.objects.filter(
            Q(sender=request.user, receiver=seller) |
            Q(sender=seller, receiver=request.user)
        ).first()

        if not match:
            match = Match.objects.create(sender=request.user, receiver=seller, product=product)

        inbox = getattr(match, 'inbox', None)
        if not inbox:
            return Response({'error': 'Chat inbox not available'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            # 'product': ProductSerializer(product, context={'request': request}).data,
            'chat': {
                'inbox_id': str(inbox.inbox_id),
                'match_id': match.id,
                'chat_user': {
                    'id': seller.id,
                    'full_name': seller.full_name,
                    'photo': seller.get_photo(),
                    'email': seller.email_address,
                }
            }
        }, status=status.HTTP_200_OK)