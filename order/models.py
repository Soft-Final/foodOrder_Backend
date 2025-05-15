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
    
    # New fields for feedback
    star_rating = models.PositiveSmallIntegerField(null=True, blank=True)
    feedback = models.TextField(null=True, blank=True)

    @classmethod
    def generate_order_number(cls):
        # Get the last order by order_number (regardless of date)
        last_order = cls.objects.order_by('-order_number').first()
        if last_order:
            try:
                last_number = int(last_order.order_number.replace('ORD-', ''))
            except (ValueError, AttributeError):
                last_number = 0
            new_number = last_number + 1
        else:
            new_number = 1
        return f"ORD-{new_number}"

    def __str__(self):
        return self.order_number
