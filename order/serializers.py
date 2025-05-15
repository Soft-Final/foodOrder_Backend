from rest_framework import serializers
from .models import Order

class OrderFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['order_number', 'star_rating', 'feedback']
        extra_kwargs = {
            'order_number': {'validators': []},  # Disable uniqueness validation for updating feedback
        }

    def validate_star_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Star rating must be between 1 and 5.")
        return value