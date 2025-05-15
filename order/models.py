from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta
import pytz

class Order(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    order_number = models.CharField(max_length=20, unique=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    items = models.JSONField()  # Store the list of item IDs and their details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')

    @classmethod
    def generate_order_number(cls):
        # Get current date in GMT+6
        gmt6 = pytz.timezone('Asia/Almaty')  # GMT+6 timezone
        current_date = timezone.now().astimezone(gmt6).date()
        
        # Get the last order number for today
        last_order = cls.objects.filter(
            created_at__date=current_date
        ).order_by('-order_number').first()
        
        if last_order:
            # Extract the number from the last order number (ORD-1 -> 1)
            last_number = int(last_order.order_number.split('-')[1])
            new_number = last_number + 1
        else:
            new_number = 1
            
        return f"ORD-{new_number}"

    def __str__(self):
        return self.order_number
