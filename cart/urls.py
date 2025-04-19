# cart/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartViewSet, CartItemViewSet, AddressViewSet, CompleteCartAPIView, CreateInvoiceAPIView, \
    AddToCartAPIView, RemoveFromCartAPIView, \
    UpdateCartItemQuantityAPIView, InvoiceViewSet

app_name = 'cart'

router = DefaultRouter()
router.register(r'cart', CartViewSet)
router.register(r'cart-items', CartItemViewSet)
router.register(r'addresses', AddressViewSet)
router.register(r'invoices', InvoiceViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('complete-cart/', CompleteCartAPIView.as_view(), name='complete-cart'),
    path('create-invoice/', CreateInvoiceAPIView.as_view(), name='create-invoice'),
    path('add-to-cart/', AddToCartAPIView.as_view(), name='add-to-cart'),
    path('remove-from-cart/', RemoveFromCartAPIView.as_view(), name='remove-from-cart'),
    path('update-cart-item-quantity/', UpdateCartItemQuantityAPIView.as_view(), name='update-cart-item-quantity'),

]
