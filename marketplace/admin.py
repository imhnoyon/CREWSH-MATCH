from django.contrib import admin
from .models import Product
# Register your models here.


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description', 'image', 'created_at', 'user')
    search_fields = ('title', 'description', 'user__full_name', 'user__email_address')
    list_filter = ('created_at',)