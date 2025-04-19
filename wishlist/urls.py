# wishlist/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WishlistViewSet

app_name = 'wishlist'

router = DefaultRouter()
router.register(r'wishlist', WishlistViewSet, basename='wishlist')

urlpatterns = [
    path('', include(router.urls)),
]
