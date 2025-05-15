from django.urls import path
from .views import CreateOrderView, UpdateOrderStatusView, GetOrderView, ListOrdersView, DeleteOrderView, PutOrderView, PatchOrderView

urlpatterns = [
    path('create/', CreateOrderView.as_view(), name='create-order'),
    path('update-status/<str:order_number>/', UpdateOrderStatusView.as_view(), name='update-order-status'),
    path('get/<str:order_number>/', GetOrderView.as_view(), name='get-order'),
    path('orders/', ListOrdersView.as_view(), name='list-orders'),
    path('delete/<str:order_number>/', DeleteOrderView.as_view(), name='delete-order'),
    path('put/<str:order_number>/', PutOrderView.as_view(), name='put-order'),
    path('patch/<str:order_number>/', PatchOrderView.as_view(), name='patch-order'),
] 