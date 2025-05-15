from django.urls import path
from .views import AnalyticsView, WeeklySalesView, MenuItemPopularityView

urlpatterns = [
    path('', AnalyticsView.as_view(), name='analytics'),
    path('weekly-sales/', WeeklySalesView.as_view(), name='weekly-sales'),
    path('menu-popularity/', MenuItemPopularityView.as_view(), name='menu-popularity'),
] 