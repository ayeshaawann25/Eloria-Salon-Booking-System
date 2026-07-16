from rest_framework import serializers
from .models import Booking
from apps.services.models import Service
from apps.users.models import User
from datetime import datetime

class BookingSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True)
    service_price = serializers.DecimalField(source='service.price', max_digits=10, decimal_places=2, read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'id', 'booking_id', 'user', 'service', 'staff', 'booking_date',
            'booking_time', 'duration', 'total_price', 'status', 'notes',
            'special_requests', 'payment_id', 'payment_status', 'created_at',
            'service_name', 'service_price', 'user_email', 'user_name'
        ]
        read_only_fields = ['booking_id', 'created_at', 'user']

class CreateBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['service', 'booking_date', 'booking_time', 'notes', 'special_requests']
    
    def validate(self, data):
        # Check if slot is already booked
        if Booking.objects.filter(
            service=data['service'],
            booking_date=data['booking_date'],
            booking_time=data['booking_time'],
            status__in=['pending', 'confirmed']
        ).exists():
            raise serializers.ValidationError("This time slot is already booked.")
        
        # Check if booking date is not in past
        if data['booking_date'] < datetime.now().date():
            raise serializers.ValidationError("Cannot book for past dates.")
        
        return data
    
    def create(self, validated_data):
        service = validated_data['service']
        validated_data['duration'] = service.duration
        validated_data['total_price'] = service.final_price
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
