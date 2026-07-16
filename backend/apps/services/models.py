from django.db import models
from django.utils import timezone
from ckeditor.fields import RichTextField

class ServiceCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)  # FontAwesome icon class
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Service Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Service(models.Model):
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=200)
    description = RichTextField()
    short_description = models.TextField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField(help_text='Duration in minutes')
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_discount = models.BooleanField(default=False)
    image = models.ImageField(upload_to='services/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-featured', 'name']
    
    def __str__(self):
        return f"{self.name} - ₹{self.price}"
    
    @property
    def final_price(self):
        return self.discount_price if self.is_discount and self.discount_price else self.price
