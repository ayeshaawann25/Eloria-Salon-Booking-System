from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['booking_id', 'user', 'service', 'booking_date', 'booking_time', 'status', 'payment_status']
    list_filter = ['status', 'payment_status', 'booking_date']
    search_fields = ['booking_id', 'user__email', 'user__phone']
    readonly_fields = ['booking_id', 'created_at', 'updated_at']
    date_hierarchy = 'booking_date'
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('booking_id', 'user', 'service', 'staff')
        }),
        ('Date & Time', {
            'fields': ('booking_date', 'booking_time', 'duration')
        }),
        ('Payment', {
            'fields': ('total_price', 'payment_id', 'payment_status')
        }),
        ('Status', {
            'fields': ('status', 'notes', 'special_requests')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

### `backend/apps/services/admin.py`
```python
from django.contrib import admin
from .models import Service, ServiceCategory
from django.utils.html import format_html

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    search_fields = ['name']
    list_filter = ['is_active']

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'duration', 'is_active', 'featured', 'discount_badge']
    list_filter = ['category', 'is_active', 'featured', 'is_discount']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    def discount_badge(self, obj):
        if obj.is_discount and obj.discount_price:
            return format_html(
                '<span style="background: #c9a87c; color: white; padding: 3px 10px; border-radius: 12px; font-size: 12px;">₹{} OFF</span>',
                obj.price - obj.discount_price
            )
        return '-'
    discount_badge.short_description = 'Discount'
