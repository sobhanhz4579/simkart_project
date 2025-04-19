# wallet/views.py
import requests
import tronpy
from django.conf import settings
from django.db import transaction
from rest_framework import generics, mixins, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from tronpy import Tron
from tronpy.providers import HTTPProvider
from .models import Transaction, Wallet
from .serializers import TransactionSerializer, WalletSerializer
from .zarinpal import ZarinPal
from cart.models import Cart


class WalletViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)


class TransactionViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                         mixins.UpdateModelMixin,
                         mixins.DestroyModelMixin,
                         viewsets.GenericViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(wallet__user=self.request.user)


class DepositTomanAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        amount = request.data.get('amount', 0)
        try:
            amount = float(amount)
            if amount <= 0:
                return Response({'detail': 'مبلغ نامعتبر است.'}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({'detail': 'مبلغ باید عدد باشد'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            wallet = request.user.wallet
        except AttributeError:
            return Response({'detail': 'کیف پول برای کاربر یافت نشد'}, status=status.HTTP_400_BAD_REQUEST)

        zarinpal_url = "https://sandbox.zarinpal.com/pg/v4/payment/request.json"
        data = {
            "merchant_id": settings.ZARINPAL_MERCHANT_ID,
            "amount": int(amount * 10),
            "description": "شارژ کیف پول (تست)",
            "callback_url": "http://localhost:8000/api/wallet/verify-toman/"
        }
        try:
            response = requests.post(zarinpal_url, json=data)
            response.raise_for_status()
            result = response.json()
        except requests.RequestException as e:
            return Response({'detail': f'خطا در اتصال به زرین‌پال: {str(e)}'},
                            status=status.HTTP_503_SERVICE_UNAVAILABLE)

        data_section = result.get("data", {})
        if data_section.get("code") == 100:
            authority = data_section["authority"]
            Transaction.objects.create(
                wallet=wallet,
                transaction_type='deposit',
                currency='toman',
                amount=amount,
                authority=authority,
                status='pending'
            )
            payment_url = f"https://sandbox.zarinpal.com/pg/StartPay/{authority}"
            return Response({
                'detail': 'لینک پرداخت',
                'payment_url': payment_url,
                'authority': authority
            })
        else:
            error_msg = result.get("errors", {}).get("message", "خطای ناشناخته")
            return Response({'detail': f'خطا از زرین‌پال: {error_msg}'}, status=status.HTTP_400_BAD_REQUEST)


###
class VerifyTomanAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def get(self, request):
        status_param = request.GET.get('Status')
        if status_param != 'OK':
            return Response({'detail': 'تراکنش لغو شد یا ناموفق بود'}, status=status.HTTP_400_BAD_REQUEST)

        authority = request.GET.get('Authority')
        if not authority:
            return Response({'detail': 'Authority دریافت نشد'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            transaction = Transaction.objects.get(authority=authority, status='pending')
        except Transaction.DoesNotExist:
            return Response({'detail': 'تراکنش پیدا نشد یا قبلاً پردازش شده است'}, status=status.HTTP_400_BAD_REQUEST)

        zarinpal_verify_url = "https://sandbox.zarinpal.com/pg/v4/payment/verify.json"
        data = {
            "merchant_id": settings.ZARINPAL_MERCHANT_ID,
            "amount": int(transaction.amount * 10),
            "authority": authority,
        }
        try:
            response = requests.post(zarinpal_verify_url, json=data)
            response.raise_for_status()
            result = response.json()
        except requests.RequestException as e:
            return Response({'detail': f'خطا در اتصال به زرین‌پال: {str(e)}'},
                            status=status.HTTP_503_SERVICE_UNAVAILABLE)

        if result.get('data', {}).get('code') == 100:
            wallet = transaction.wallet
            wallet.balance_toman += transaction.amount
            wallet.save()
            transaction.status = 'completed'
            transaction.save()
            return Response({
                'detail': 'واریز موفقیت‌آمیز',
                'balance_toman': wallet.balance_toman
            })
        elif result.get('data', {}).get('code') == 101:
            return Response({'detail': 'این تراکنش قبلاً تأیید شده است'}, status=status.HTTP_200_OK)
        else:
            error_message = result.get('errors', {}).get('message', 'خطای ناشناخته از زرین‌پال')
            return Response({'detail': f"پرداخت ناموفق: {error_message}"}, status=status.HTTP_400_BAD_REQUEST)


class DepositTRXAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            wallet = request.user.wallet
        except AttributeError:
            return Response({'detail': 'کیف پول برای کاربر یافت نشد'}, status=status.HTTP_400_BAD_REQUEST)
        if not wallet.trx_address:
            return Response({'detail': 'آدرس TRX برای این کیف پول تنظیم نشده است'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail': 'آدرس واریز TRX', 'trx_address': wallet.trx_address})


class VerifyTRXDepositAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        tx_hash = request.data.get('tx_hash')
        if not tx_hash:
            return Response({'detail': 'لطفاً کد تراکنش را وارد کنید.'}, status=status.HTTP_400_BAD_REQUEST)

        client = Tron(network='shasta', provider=HTTPProvider('https://api.shasta.trongrid.io'))
        try:
            tx_info = client.get_transaction(tx_hash)
        except Exception as e:
            return Response({'detail': f'خطا در بررسی تراکنش: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        if tx_info['ret'][0]['contractRet'] == 'SUCCESS' and 'contract' in tx_info['raw_data']:
            contract = tx_info['raw_data']['contract'][0]
            if contract['type'] == 'TransferContract':
                amount = contract['parameter']['value']['amount'] / 1_000_000

                try:
                    wallet = request.user.wallet
                except AttributeError:
                    return Response({'detail': 'کیف پول برای کاربر یافت نشد'}, status=status.HTTP_400_BAD_REQUEST)

                if contract['parameter']['value']['to_address'] == wallet.trx_address:
                    wallet.balance_trx += amount
                    wallet.save()
                    Transaction.objects.create(
                        wallet=wallet,
                        transaction_type='deposit',
                        currency='trx',
                        amount=amount,
                        tx_hash=tx_hash,
                        status='completed'
                    )
                    return Response({'detail': 'واریز موفقیت‌آمیز', 'balance_trx': wallet.balance_trx})
                return Response({'detail': 'آدرس مقصد تراکنش با کیف پول شما مطابقت ندارد.'},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response({'detail': 'تراکنش نامعتبر - فقط انتقال TRX پشتیبانی می‌شود'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail': 'تراکنش نامعتبر'}, status=status.HTTP_400_BAD_REQUEST)


class PayCartAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        cart = Cart.objects.filter(user=request.user, status='pending').first()
        if not cart:
            return Response({'detail': 'سبد خرید پیدا نشد.'}, status=status.HTTP_404_NOT_FOUND)
        total_price = cart.total_price()
        payment_method = request.data.get('method')
        try:
            wallet = request.user.wallet
        except AttributeError:
            return Response({'detail': 'کیف پول برای کاربر یافت نشد'}, status=status.HTTP_400_BAD_REQUEST)

        if payment_method == 'toman':
            if wallet.balance_toman < total_price:
                return Response({'detail': 'موجودی کافی نیست.'}, status=status.HTTP_400_BAD_REQUEST)
            with transaction.atomic():
                wallet.balance_toman -= float(total_price)
                wallet.save()
                Transaction.objects.create(
                    wallet=wallet,
                    transaction_type='payment',
                    currency='toman',
                    amount=total_price,
                    description=f"پرداخت سبد خرید {cart.id} با کیف پول",
                    status='completed'
                )
                cart.status = 'completed'
                cart.save()
            return Response({'detail': 'پرداخت با موفقیت انجام شد.'})
        elif payment_method == 'trx':
            if wallet.balance_trx < total_price:
                return Response({'detail': 'موجودی کافی نیست.'}, status=status.HTTP_400_BAD_REQUEST)
            with transaction.atomic():
                wallet.balance_trx -= float(total_price)
                wallet.save()
                Transaction.objects.create(
                    wallet=wallet,
                    transaction_type='payment',
                    currency='trx',
                    amount=total_price,
                    description=f"پرداخت سبد خرید {cart.id} با کیف پول",
                    status='completed'
                )
                cart.status = 'completed'
                cart.save()
            return Response({'detail': 'پرداخت با موفقیت انجام شد.'})
        elif payment_method == 'direct_toman':
            zarinpal = ZarinPal(settings.ZARINPAL_MERCHANT_ID,
                                "http://localhost:8000/api/wallet/verify-direct-zarinpal/")
            try:
                result = zarinpal.send_request(total_price, f"پرداخت مستقیم سبد خرید {cart.id}",
                                               email=request.user.email or "example@email.com")
            except Exception as e:
                return Response({'detail': f'خطا در درخواست زرین‌پال: {str(e)}'},
                                status=status.HTTP_503_SERVICE_UNAVAILABLE)
            if result['status'] == 'success':
                Transaction.objects.create(
                    wallet=wallet,
                    transaction_type='payment',
                    currency='toman',
                    amount=total_price,
                    description=f"Direct Zarinpal: Authority {result['authority']}",
                    status='pending'
                )
                return Response({'detail': 'لینک پرداخت', 'payment_url': result['payment_url']})
            return Response({'detail': result['message'], 'error_code': result['error_code']},
                            status=status.HTTP_400_BAD_REQUEST)
        elif payment_method == 'direct_trx':
            if not wallet.trx_address:
                return Response({'detail': 'آدرس TRX برای این کیف پول تنظیم نشده است'},
                                status=status.HTTP_400_BAD_REQUEST)
            Transaction.objects.create(
                wallet=wallet,
                transaction_type='payment',
                currency='trx',
                amount=total_price,
                description=f"پرداخت مستقیم سبد خرید {cart.id} - در انتظار تأیید",
                status='pending'
            )
            return Response({'detail': 'آدرس واریز TRX', 'trx_address': wallet.trx_address, 'amount': total_price})
        return Response({'detail': 'روش پرداخت نامعتبر'}, status=status.HTTP_400_BAD_REQUEST)


class VerifyDirectZarinpal(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def get(self, request, *args, **kwargs):
        if request.GET.get('Status') != 'OK':
            return Response({'detail': 'تراکنش لغو شده یا ناموفق بود'}, status=400)
        authority = request.GET.get('Authority')
        try:
            transaction = Transaction.objects.get(description__contains=authority, status='pending')
        except Transaction.DoesNotExist:
            return Response({'detail': 'تراکنش پیدا نشد یا قبلاً پردازش شده است'}, status=status.HTTP_400_BAD_REQUEST)

        zarinpal = ZarinPal(settings.ZARINPAL_MERCHANT_ID, "http://localhost:8000/api/wallet/verify-direct-zarinpal/")
        try:
            result = zarinpal.verify(authority, transaction.amount)
        except Exception as e:
            return Response({'detail': f'خطا در تأیید پرداخت: {str(e)}'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        if result['status'] == 'success':
            cart = Cart.objects.filter(user=request.user, status='pending').first()
            if cart:
                cart.status = 'completed'
                cart.save()
            transaction.status = 'completed'
            transaction.description += f" - RefID: {result['ref_id']}"
            transaction.save()
            return Response({'detail': 'پرداخت مستقیم با موفقیت انجام شد'})
        return Response({'detail': 'پرداخت ناموفق', 'message': result['message']}, status=status.HTTP_400_BAD_REQUEST)


class VerifyDirectPayCartTRXAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        tx_hash = request.data.get('tx_hash')
        print("tx_hash received:", tx_hash)
        if not tx_hash or len(tx_hash) != 64 or not tx_hash.isalnum():
            return Response({'detail': 'هش تراکنش نامعتبر است. باید ۶۴ کاراکتر هگزادسیمال باشد.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if Transaction.objects.filter(tx_hash=tx_hash, status='completed').exists():
            return Response({'detail': 'این تراکنش قبلاً پردازش شده است'}, status=status.HTTP_400_BAD_REQUEST)

        cart = Cart.objects.filter(user=request.user, status='pending').first()
        if not cart:
            return Response({'detail': 'سبد خرید پیدا نشد.'}, status=status.HTTP_404_NOT_FOUND)

        tron = Tron(network='shasta', provider=HTTPProvider('https://api.shasta.trongrid.io'))
        try:
            tx_info = tron.get_transaction(tx_hash)
        except Exception as e:
            return Response({'detail': f'خطا در بررسی تراکنش: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        if tx_info['ret'][0]['contractRet'] == 'SUCCESS' and 'contract' in tx_info['raw_data']:
            contract = tx_info['raw_data']['contract'][0]
            if contract['type'] == 'TransferContract':
                amount = contract['parameter']['value']['amount'] / 1_000_000
                try:
                    wallet = request.user.wallet
                    if not wallet.trx_address:
                        return Response({'detail': 'آدرس TRX برای این کیف پول تنظیم نشده است'},
                                        status=status.HTTP_400_BAD_REQUEST)
                except AttributeError:
                    return Response({'detail': 'کیف پول برای کاربر یافت نشد'}, status=status.HTTP_400_BAD_REQUEST)

                if contract['parameter']['value']['to_address'] == wallet.trx_address and amount >= cart.total_price():
                    transactions = Transaction.objects.filter(
                        wallet=wallet,
                        status='pending',
                        description__contains=f"پرداخت مستقیم سبد خرید {cart.id}"
                    )
                    if not transactions.exists():
                        return Response({'detail': 'تراکنش پیدا نشد یا قبلاً پردازش شده است'},
                                        status=status.HTTP_400_BAD_REQUEST)

                    transaction = transactions.first()
                    transaction.status = 'completed'
                    transaction.tx_hash = tx_hash
                    transaction.save()
                    cart.status = 'completed'
                    cart.save()
                    return Response({'detail': 'پرداخت مستقیم با موفقیت انجام شد'})
                return Response({'detail': 'مقدار یا آدرس تراکنش نامعتبر است'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'detail': 'تراکنش نامعتبر - فقط انتقال TRX پشتیبانی می‌شود'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail': 'تراکنش نامعتبر'}, status=status.HTTP_400_BAD_REQUEST)
