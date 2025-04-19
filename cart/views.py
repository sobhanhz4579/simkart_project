# cart/views.py
from rest_framework import permissions, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Cart, CartItem, Address, Invoice
from .serializers import CartSerializer, CartItemSerializer, AddressSerializer, InvoiceSerializer
from django.db import transaction


class IsAdminOrOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_staff:
            return True
        return view.get_object().user == request.user


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]


class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]


class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CompleteCartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        cart = Cart.objects.filter(user=request.user, status='pending').first()

        if not cart:
            return Response({'detail': 'سبد خرید پیدا نشد یا قبلاً تکمیل شده است.'}, status=status.HTTP_404_NOT_FOUND)

        address = Address.objects.filter(user=request.user).first()
        if not address:
            return Response({'detail': 'لطفاً ابتدا آدرس خود را ثبت کنید.'}, status=status.HTTP_400_BAD_REQUEST)

        if not cart.items.exists():
            return Response({'detail': 'سبد خرید شما خالی است.'}, status=status.HTTP_400_BAD_REQUEST)

        cart.status = 'completed'
        cart.save()

        return Response({'detail': 'سبد خرید با موفقیت تکمیل شد.'}, status=status.HTTP_200_OK)


class CreateOrUpdateAddressAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = AddressSerializer(data=request.data)

        if serializer.is_valid():
            Address.objects.update_or_create(
                user=request.user,
                defaults=serializer.validated_data
            )
            return Response({'detail': 'آدرس شما با موفقیت ثبت شد.'}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateInvoiceAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        cart = Cart.objects.filter(user=request.user, status='completed').first()

        if not cart:
            return Response({'detail': 'سبد خرید پیدا نشد یا تکمیل نشده است.'}, status=status.HTTP_404_NOT_FOUND)

        if Invoice.objects.filter(cart=cart).exists():
            return Response({'detail': 'فاکتور این سبد خرید قبلاً ایجاد شده است.'}, status=status.HTTP_400_BAD_REQUEST)

        invoice = Invoice.objects.create(cart=cart, amount=cart.total_price)

        return Response({'detail': f'فاکتور با موفقیت ایجاد شد. مبلغ کل: {invoice.amount}'},
                        status=status.HTTP_201_CREATED)


class AddToCartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        simcard_id = request.data.get('simcard_id')

        if not simcard_id:
            return Response({'detail': 'لطفاً شناسه محصول را وارد کنید.'}, status=status.HTTP_400_BAD_REQUEST)

        cart, created = Cart.objects.get_or_create(user=request.user, status='pending')
        cart_item, created = CartItem.objects.get_or_create(cart=cart, simcard_id=simcard_id)
        if not created:
            cart_item.quantity += 1
            cart_item.save()

        return Response({'detail': 'محصول به سبد خرید اضافه شد.'}, status=status.HTTP_200_OK)


class RemoveFromCartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        simcard_id = request.data.get('simcard_id')

        if not simcard_id:
            return Response({'detail': 'لطفاً شناسه محصول را وارد کنید.'}, status=status.HTTP_400_BAD_REQUEST)

        cart = Cart.objects.filter(user=request.user, status='pending').first()

        if not cart:
            return Response({'detail': 'سبد خرید پیدا نشد.'}, status=status.HTTP_404_NOT_FOUND)

        cart_item = CartItem.objects.filter(cart=cart, simcard_id=simcard_id).first()

        if not cart_item:
            return Response({'detail': 'محصول در سبد خرید یافت نشد.'}, status=status.HTTP_404_NOT_FOUND)

        cart_item.delete()
        return Response({'detail': 'محصول از سبد خرید حذف شد.'}, status=status.HTTP_200_OK)


class UpdateCartItemQuantityAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        simcard_id = request.data.get('simcard_id')
        quantity = request.data.get('quantity', 1)

        if not simcard_id or quantity < 1:
            return Response({'detail': 'لطفاً شناسه محصول و تعداد معتبر وارد کنید.'},
                            status=status.HTTP_400_BAD_REQUEST)

        cart = Cart.objects.filter(user=request.user, status='pending').first()
        if not cart:
            return Response({'detail': 'سبد خرید پیدا نشد.'}, status=status.HTTP_404_NOT_FOUND)

        cart_item = CartItem.objects.filter(cart=cart, simcard_id=simcard_id).first()
        if not cart_item:
            return Response({'detail': 'محصول در سبد خرید یافت نشد.'}, status=status.HTTP_404_NOT_FOUND)

        cart_item.quantity = quantity
        cart_item.save()
        return Response({'detail': 'تعداد محصول به‌روزرسانی شد.'}, status=status.HTTP_200_OK)


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Invoice.objects.filter(cart__user=self.request.user)
