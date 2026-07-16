from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.services.models import Service

class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    )
    
    booking_id = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='bookings')
    staff = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_bookings')
    
    booking_date = models.DateField()
    booking_time = models.TimeField()
    duration = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    special_requests = models.TextField(blank=True)
    
    # Payment
    payment_id = models.CharField(max_length=100, blank=True)
    payment_status = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['booking_date', 'booking_time', 'service']
        ordering = ['-booking_date', '-booking_time']
    
    def __str__(self):
        return f"{self.booking_id} - {self.user.email} - {self.booking_date}"
    
    def save(self, *args, **kwargs):
        if not self.booking_id:
            # Generate booking ID: ELORIA-2024-001
            date_str = timezone.now().strftime('%Y%m%d')
            last_booking = Booking.objects.filter(booking_id__startswith=f'ELORIA-{date_str}').order_by('created_at').last()
            if last_booking:
                last_num = int(last_booking.booking_id.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            self.booking_id = f'ELORIA-{date_str}-{str(new_num).zfill(3)}'
        super().save(*args, **kwargs)
