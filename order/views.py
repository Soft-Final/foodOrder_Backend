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
from rest_framework.generics import RetrieveAPIView
from .serializers import OrderFeedbackSerializer
from django.db.models import Avg

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

class GetOrderView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, order_number, *args, **kwargs):
        try:
            order = Order.objects.get(order_number=order_number)
            return Response({
                'order_number': order.order_number,
                'total_price': str(order.total_price),
                'created_at': order.created_at,
                'items': order.items,
                'status': order.status,
                'star_rating': order.star_rating,
                'feedback': order.feedback,
            }, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

class ListOrdersView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        orders = Order.objects.all().order_by('-created_at')
        data = [
            {
                'order_number': order.order_number,
                'total_price': str(order.total_price),
                'created_at': order.created_at,
                'items': order.items,
                'status': order.status,
                'star_rating': order.star_rating,
                'feedback': order.feedback,
            }
            for order in orders
        ]
        return Response(data, status=status.HTTP_200_OK)

class DeleteOrderView(APIView):
    permission_classes = [AllowAny]

    def delete(self, request, order_number, *args, **kwargs):
        try:
            order = Order.objects.get(order_number=order_number)
            order.delete()
            return Response({'message': 'Order deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

class PutOrderView(APIView):
    permission_classes = [AllowAny]

    def put(self, request, order_number, *args, **kwargs):
        try:
            order = Order.objects.get(order_number=order_number)
            data = request.data
            # Update all fields (except order_number and created_at)
            order.total_price = data.get('total_price', order.total_price)
            order.items = data.get('items', order.items)
            order.status = data.get('status', order.status)
            order.save()
            return Response({'message': 'Order updated successfully'}, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

class PatchOrderView(APIView):
    permission_classes = [AllowAny]

    def patch(self, request, order_number, *args, **kwargs):
        try:
            order = Order.objects.get(order_number=order_number)
            data = request.data
            # Update only provided fields
            if 'total_price' in data:
                order.total_price = data['total_price']
            if 'items' in data:
                order.items = data['items']
            if 'status' in data:
                order.status = data['status']
            order.save()
            return Response({'message': 'Order partially updated successfully'}, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

class OrderFeedbackAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = OrderFeedbackSerializer(data=request.data)
        if serializer.is_valid():
            order_number = serializer.validated_data.get("order_number")
            try:
                order = Order.objects.get(order_number=order_number)
            except Order.DoesNotExist:
                return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

            order.star_rating = serializer.validated_data.get("star_rating")
            order.feedback = serializer.validated_data.get("feedback")
            order.save()

            return Response({"message": "Feedback updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AverageRatingAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        # Calculate the average star rating for orders that have a rating
        avg_rating = Order.objects.filter(star_rating__isnull=False).aggregate(average=Avg('star_rating'))['average']
        if avg_rating is None:
            avg_rating = 0  # or return a message indicating no ratings available
        return Response({"average_rating": avg_rating}, status=status.HTTP_200_OK)
