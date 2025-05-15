from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'total_price', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('order_number',)
    readonly_fields = ('order_number', 'created_at')
    ordering = ('-created_at',)

    def has_add_permission(self, request):
        # Prevent manual creation of orders through admin
        return False
