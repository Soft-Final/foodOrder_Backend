from django.urls import path
from .views import CreateOrderView, UpdateOrderStatusView

urlpatterns = [
    path('create/', CreateOrderView.as_view(), name='create-order'),
    path('update-status/<str:order_number>/', UpdateOrderStatusView.as_view(), name='update-order-status'),
] 