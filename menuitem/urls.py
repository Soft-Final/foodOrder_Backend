from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MenuItemViewSet, AnalyticsView

router = DefaultRouter()
router.register(r'items', MenuItemViewSet, basename='menuitem')

urlpatterns = [
    path('', include(router.urls)),
    path('analytics/', AnalyticsView.as_view(), name='analytics'),
]