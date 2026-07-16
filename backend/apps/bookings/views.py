from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Booking
from .serializers import BookingSerializer, CreateBookingSerializer
from apps.services.models import Service
from apps.users.permissions import IsAdminOrStaff
from .tasks import send_booking_confirmation_email

class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'staff']:
            return Booking.objects.all()
        return Booking.objects.filter(user=user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CreateBookingSerializer
        return BookingSerializer
    
    def perform_create(self, serializer):
        booking = serializer.save()
        # Send confirmation email asynchronously
        send_booking_confirmation_email.delay(booking.id)
    
    @action(detail=False, methods=['get'])
    def available_slots(self, request):
        """Get available time slots for a specific date and service"""
        service_id = request.query_params.get('service')
        date = request.query_params.get('date')
        
        if not service_id or not date:
            return Response(
                {'error': 'Service ID and date are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            service = Service.objects.get(id=service_id)
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        except Service.DoesNotExist:
            return Response(
                {'error': 'Service not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError:
            return Response(
                {'error': 'Invalid date format'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate all time slots (9 AM to 8 PM)
        all_slots = []
        start_time = datetime.strptime('09:00', '%H:%M')
        end_time = datetime.strptime('20:00', '%H:%M')
        slot_duration = service.duration
        
        current_time = start_time
        while current_time <= end_time:
            all_slots.append(current_time.strftime('%H:%M'))
            current_time += timedelta(minutes=slot_duration)
        
        # Get booked slots
        booked_slots = Booking.objects.filter(
            service=service,
            booking_date=date_obj,
            status__in=['pending', 'confirmed']
        ).values_list('booking_time', flat=True)
        
        booked_times = [slot.strftime('%H:%M') for slot in booked_slots]
        
        available_slots = [slot for slot in all_slots if slot not in booked_times]
        
        return Response({
            'date': date,
            'service': service.name,
            'available_slots': available_slots,
            'booked_slots': booked_times
        })
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        
        # Check if booking can be cancelled
        if booking.status in ['completed', 'cancelled']:
            return Response(
                {'error': 'This booking cannot be cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if cancellation is within 24 hours
        time_diff = booking.booking_date - timezone.now().date()
        if time_diff.days < 1 and booking.booking_time < timezone.now().time():
            return Response(
                {'error': 'Cannot cancel booking within 24 hours'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.status = 'cancelled'
        booking.save()
        
        return Response({'success': 'Booking cancelled successfully'})
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming bookings for the current user"""
        today = timezone.now().date()
        bookings = self.get_queryset().filter(
            booking_date__gte=today,
            status__in=['pending', 'confirmed']
        ).order_by('booking_date', 'booking_time')
        
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get booking history for the current user"""
        bookings = self.get_queryset().filter(
            status__in=['completed', 'cancelled']
        ).order_by('-booking_date', '-booking_time')
        
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)
