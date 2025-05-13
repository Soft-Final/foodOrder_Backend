from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum
from .models import MenuItem
from .serializers import MenuItemSerializer

# Helper methods to check user types
def is_kitchen(user):
    return user.is_authenticated and user.user_type == 'KITCHEN'

def is_admin(user):
    return user.is_authenticated and (user.is_admin or user.is_superuser)

class MenuItemViewSet(viewsets.ModelViewSet):
    """
    GET (list/retrieve): Publicly accessible.
    POST, PUT, PATCH, DELETE: Restricted to kitchen staff.
    """
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        if not is_kitchen(request.user):
            return Response({"error": "Only kitchen staff can create menu items."},
                            status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if not is_kitchen(request.user):
            return Response({"error": "Only kitchen staff can update menu items."},
                            status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not is_kitchen(request.user):
            return Response({"error": "Only kitchen staff can delete menu items."},
                            status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

class AnalyticsView(APIView):
    """
    Admin-only view for analytics.
    Query parameter 'period' can be 'day', 'week', or 'month' to filter the data.
    Returns the most purchased menu item and aggregated total cancelled orders.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if not is_admin(request.user):
            return Response({"error": "Only admins can access analytics."},
                            status=status.HTTP_403_FORBIDDEN)
        period = request.query_params.get('period', None)
        now = timezone.now()
        start_date = None
        if period == 'day':
            start_date = now - timedelta(days=1)
        elif period == 'week':
            start_date = now - timedelta(weeks=1)
        elif period == 'month':
            start_date = now - timedelta(days=30)

        items = MenuItem.objects.all()
        if start_date:
            items = items.filter(created_at__gte=start_date)

        # Determine the item with the highest order_count
        most_purchased = items.order_by('-order_count').first()
        most_purchased_data = MenuItemSerializer(most_purchased).data if most_purchased else {}

        # Aggregate total cancelled orders from the filtered items
        total_cancelled = items.aggregate(total=Sum('cancelled_order_count'))['total'] or 0

        return Response({
            "most_purchased_item": most_purchased_data,
            "total_cancelled_orders": total_cancelled,
        })
