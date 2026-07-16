from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.services.models import Service, ServiceCategory
from apps.bookings.models import Booking
from datetime import datetime, timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed initial data for Eloria Salon'
    
    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')
        
        # Create admin user
        if not User.objects.filter(email='admin@eloria.com').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@eloria.com',
                password='admin123',
                phone='9876543210',
                role='admin'
            )
            self.stdout.write('✅ Admin user created')
        
        # Create categories
        categories = [
            {'name': 'Hair Services', 'icon': 'fa-cut'},
            {'name': 'Skin Care', 'icon': 'fa-spa'},
            {'name': 'Nail Art', 'icon': 'fa-paint-brush'},
            {'name': 'Makeup', 'icon': 'fa-crown'},
            {'name': 'Massage', 'icon': 'fa-hands'},
        ]
        
        for cat_data in categories:
            category, created = ServiceCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={'icon': cat_data['icon']}
            )
            if created:
                self.stdout.write(f'✅ Category created: {category.name}')
        
        # Create services
        services_data = [
            {'category': 'Hair Services', 'name': 'Haircut & Styling', 'price': 1200, 'duration': 60},
            {'category': 'Hair Services', 'name': 'Hair Color', 'price': 2500, 'duration': 120},
            {'category': 'Skin Care', 'name': 'Facial Treatment', 'price': 1800, 'duration': 75},
            {'category': 'Skin Care', 'name': 'Anti-Aging Therapy', 'price': 3000, 'duration': 90},
            {'category': 'Nail Art', 'name': 'Basic Manicure', 'price': 900, 'duration': 45},
            {'category': 'Nail Art', 'name': 'Premium Nail Art', 'price': 1500, 'duration': 60},
            {'category': 'Makeup', 'name': 'Bridal Makeup', 'price': 4500, 'duration': 120},
            {'category': 'Makeup', 'name': 'Party Makeup', 'price': 2500, 'duration': 90},
            {'category': 'Massage', 'name': 'Swedish Massage', 'price': 2000, 'duration': 60},
            {'category': 'Massage', 'name': 'Deep Tissue Massage', 'price': 2500, 'duration': 60},
        ]
        
        for service_data in services_data:
            category = ServiceCategory.objects.get(name=service_data['category'])
            service, created = Service.objects.get_or_create(
                name=service_data['name'],
                category=category,
                defaults={
                    'price': service_data['price'],
                    'duration': service_data['duration'],
                    'short_description': f'Professional {service_data["name"].lower()} service',
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'✅ Service created: {service.name}')
        
        self.stdout.write(self.style.SUCCESS('🎉 Data seeding completed!'))
