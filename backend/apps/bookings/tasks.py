from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import Booking

@shared_task
def send_booking_confirmation_email(booking_id):
    """Send booking confirmation email asynchronously"""
    try:
        booking = Booking.objects.get(id=booking_id)
        subject = f"Booking Confirmation - {booking.booking_id}"
        
        context = {
            'booking': booking,
            'service': booking.service,
            'user': booking.user,
            'site_url': settings.CLIENT_URL
        }
        
        html_message = render_to_string('emails/booking_confirmation.html', context)
        plain_message = f"Your booking has been confirmed. Booking ID: {booking.booking_id}"
        
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [booking.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return f"Email sent to {booking.user.email}"
    except Booking.DoesNotExist:
        return "Booking not found"

@shared_task
def send_reminder_emails():
    """Send reminder emails for tomorrow's bookings"""
    tomorrow = timezone.now().date() + timedelta(days=1)
    bookings = Booking.objects.filter(
        booking_date=tomorrow,
        status='confirmed'
    ).select_related('user', 'service')
    
    for booking in bookings:
        send_booking_reminder_email.delay(booking.id)
    
    return f"Sent {bookings.count()} reminder emails"

@shared_task
def send_booking_reminder_email(booking_id):
    """Send reminder email for a specific booking"""
    try:
        booking = Booking.objects.get(id=booking_id)
        subject = f"Reminder: Your Eloria appointment tomorrow"
        
        context = {
            'booking': booking,
            'service': booking.service,
        }
        
        html_message = render_to_string('emails/booking_reminder.html', context)
        
        send_mail(
            subject,
            f"Reminder for your booking on {booking.booking_date} at {booking.booking_time}",
            settings.DEFAULT_FROM_EMAIL,
            [booking.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return f"Reminder sent to {booking.user.email}"
    except Booking.DoesNotExist:
        return "Booking not found"
