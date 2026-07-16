from rest_framework import serializers
from .models import Service, ServiceCategory

class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ['id', 'name', 'description', 'icon', 'is_active', 'created_at']

class ServiceSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Service
        fields = [
            'id', 'category', 'category_name', 'name', 'description',
            'short_description', 'price', 'duration', 'discount_price',
            'is_discount', 'image', 'is_active', 'featured', 'final_price',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class ServiceListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Service
        fields = ['id', 'name', 'short_description', 'final_price', 'duration', 'image', 'category_name', 'featured']
