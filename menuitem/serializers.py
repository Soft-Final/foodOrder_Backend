from rest_framework import serializers
from .models import Category, MenuItem

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class MenuItemSerializer(serializers.ModelSerializer):
    # For read operations, include category details.
    category = CategorySerializer(read_only=True)
    # For write operations, accept a category ID.
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category', write_only=True)
    
    class Meta:
        model = MenuItem
        fields = [
            'id', 'name', 'price', 'image', 'is_available', 'description',
            'category', 'category_id', 'order_count', 'cancelled_order_count'
        ]
        read_only_fields = ['order_count', 'cancelled_order_count']