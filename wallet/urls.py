# wallet/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (WalletViewSet, TransactionViewSet, DepositTomanAPIView, VerifyTomanAPIView, DepositTRXAPIView,
                    VerifyTRXDepositAPIView,
                    PayCartAPIView,
                    VerifyDirectZarinpal,
                    VerifyDirectPayCartTRXAPIView,
                    )

router = DefaultRouter()
router.register(r'wallet', WalletViewSet, basename='wallet')
router.register(r'transactions', TransactionViewSet, basename='transaction')

app_name = 'wallet'

urlpatterns = [
    path('', include(router.urls)),
    path('deposit-toman/', DepositTomanAPIView.as_view(), name='deposit-toman'),
    path('verify-toman/', VerifyTomanAPIView.as_view(), name='verify-toman'),
    path('deposit-trx/', DepositTRXAPIView.as_view(), name='deposit-trx'),
    path('verify-trx/', VerifyTRXDepositAPIView.as_view(), name='verify-trx'),
    path('pay-cart/', PayCartAPIView.as_view(), name='pay-cart'),
    path('verify-direct-zarinpal/', VerifyDirectZarinpal.as_view(), name='verify-direct-zarinpal'),
    path('verify-direct-trx/', VerifyDirectPayCartTRXAPIView.as_view(), name='verify-direct-trx'),
]
