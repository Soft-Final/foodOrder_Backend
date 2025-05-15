from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Order
from menuitem.models import MenuItem
from decimal import Decimal
from django.db import transaction, models
from rest_framework.permissions import BasePermission

# Create your views here.

class IsKitchenUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'KITCHEN'

class CreateOrderView(APIView):
    permission_classes = [AllowAny]  # Allow anyone to create orders

    def post(self, request, *args, **kwargs):
        item_ids = request.data.get('items', [])
        
        if not item_ids:
            return Response(
                {"error": "No items provided"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Use transaction to ensure data consistency
            with transaction.atomic():
                # Get all menu items in one query
                menu_items = MenuItem.objects.filter(id__in=item_ids)
                
                # Create a dictionary for quick price lookup
                item_prices = {item.id: item.price for item in menu_items}
                
                # Calculate total price
                total_price = sum(item_prices.get(item_id, 0) for item_id in item_ids)
                
                # Create order
                order = Order.objects.create(
                    order_number=Order.generate_order_number(),
                    total_price=total_price,
                    items={
                        'item_ids': item_ids,
                        'item_details': [
                            {
                                'id': item.id,
                                'name': item.name,
                                'price': str(item.price)
                            } for item in menu_items
                        ]
                    }
                )

                # Increment order_count for each menu item
                for item_id in item_ids:
                    MenuItem.objects.filter(id=item_id).update(
                        order_count=models.F('order_count') + 1
                    )
                
                return Response({
                    'order_number': order.order_number,
                    'total_price': str(order.total_price)
                }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class UpdateOrderStatusView(APIView):
    permission_classes = [IsAuthenticated, IsKitchenUser]

    def patch(self, request, order_number, *args, **kwargs):
        new_status = request.data.get('status')
        
        if not new_status or new_status not in dict(Order.STATUS_CHOICES):
            return Response(
                {"error": "Invalid status. Must be either 'in_progress' or 'completed'"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            order = Order.objects.get(order_number=order_number)
            order.status = new_status
            order.save()
            
            return Response({
                'order_number': order.order_number,
                'status': order.status
            }, status=status.HTTP_200_OK)
            
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
