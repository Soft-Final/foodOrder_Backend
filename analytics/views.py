from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import datetime, timedelta
from order.models import Order
from menuitem.models import MenuItem
from django.db.models import Count, F, ExpressionWrapper, FloatField, Sum
from django.db.models.functions import TruncDate

# Create your views here.

class AnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get the first day of current month
        today = timezone.now()
        first_day_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Get total orders from start of month until now
        total_orders = Order.objects.filter(
            created_at__gte=first_day_of_month,
            created_at__lte=today
        ).count()

        # Get active (in_progress) orders
        active_orders = Order.objects.filter(status='in_progress').count()

        # Get total menu items
        menu_items = MenuItem.objects.count()

        return Response({
            'total_orders': total_orders,
            'active_orders': active_orders,
            'menu_items': menu_items
        })

class WeeklySalesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get the start of the current week (Monday)
        today = timezone.now()
        start_of_week = today - timedelta(days=today.weekday())
        start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)

        # Get orders for each day of the week
        daily_orders = Order.objects.filter(
            created_at__gte=start_of_week,
            created_at__lte=today
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')

        # Create a dictionary with all days of the week initialized to 0
        week_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        sales_data = {day: 0 for day in week_days}

        # Fill in the actual order counts
        for order_data in daily_orders:
            day_name = order_data['date'].strftime('%A')
            sales_data[day_name] = order_data['count']

        return Response({
            'weekly_sales': sales_data,
            'week_start': start_of_week.date(),
            'week_end': today.date()
        })

class MenuItemPopularityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get the first day of current month
        today = timezone.now()
        first_day_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Get total items ordered this month (sum of all order_count)
        total_items_ordered = MenuItem.objects.aggregate(
            total=Sum('order_count')
        )['total'] or 0

        if total_items_ordered == 0:
            return Response({
                'message': 'No items ordered this month',
                'popular_items': []
            })

        # Get menu items with their order counts
        popular_items = MenuItem.objects.values('name', 'order_count').order_by('-order_count')[:4]

        # Calculate percentages and format the response
        formatted_items = [
            {
                'name': item['name'],
                'order_count': item['order_count'],
                'percentage': round((item['order_count'] / total_items_ordered) * 100, 2)
            }
            for item in popular_items
        ]

        return Response({
            'total_items_ordered': total_items_ordered,
            'popular_items': formatted_items
        })
