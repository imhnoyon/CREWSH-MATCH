from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'image', 'created_at', 'user']
    
    def get_user(self, obj):
        return {
            'id': obj.user.id,
            'username': obj.user.full_name,
            'email': obj.user.email_address,
            'photo': obj.user.get_photo()   
        }