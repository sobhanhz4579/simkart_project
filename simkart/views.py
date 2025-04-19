# simkart/views.py
import logging
import random
import string
from django.conf import settings
from django.contrib.auth import get_user_model, logout
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import UpdateAPIView, GenericAPIView
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.tokens import RefreshToken
from taggit.models import Tag
from .models import SimCard, Comment, Account
from .permissions import IsAdminOrReadOnly
from .serializers import (
    SimCardSerializer,
    CommentSerializer,
    RegisterSerializer,
    UserSerializer,
    ChangePasswordSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer,
    ContactSerializer
)
from .utils import (
    send_share_email,
    generate_whatsapp_link,
    generate_facebook_link,
    generate_twitter_link
)

search_logger = logging.getLogger('search_logger')


class SimCardPagination(PageNumberPagination):
    page_size = 4
    page_size_query_param = 'page_size'
    max_page_size = 100


User = get_user_model()


class RegisterSend(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_data = serializer.validated_data
        verification_code = ''.join(random.choices(string.digits, k=6))
        request.session['verification_code'] = verification_code
        request.session['user_data'] = user_data
        send_mail(
            'ثبت‌نام در سایت سیم‌کارت',
            f'کد تایید شما: {verification_code}',
            settings.DEFAULT_FROM_EMAIL,
            [user_data['email']],
            fail_silently=False,
        )
        return Response({
            'message': 'اطلاعات شما ارسال شد. کد تایید به ایمیل شما ارسال گردید.'
        }, status=status.HTTP_200_OK)


class RegisterVerified(generics.GenericAPIView):
    permission_classes = []
    serializer_class = RegisterSerializer

    @transaction.atomic
    def post(self, request):
        code = request.data.get('code')
        stored_code = request.session.get('verification_code')
        user_data = request.session.get('user_data')
        if not stored_code or not user_data:
            return Response({'error': 'اطلاعات یا کد تایید یافت نشد.'}, status=status.HTTP_400_BAD_REQUEST)
        if code == stored_code:
            serializer = self.get_serializer(data=user_data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            account, created = Account.objects.get_or_create(user=user)
            del request.session['verification_code']
            del request.session['user_data']
            return Response({'message': 'ثبت‌نام شما با موفقیت انجام شد.'}, status=status.HTTP_201_CREATED)
        return Response({'error': 'کد وارد شده اشتباه است.'}, status=status.HTTP_400_BAD_REQUEST)


class LoginSend(generics.GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(User, username=serializer.validated_data['username'])
        if not user.check_password(serializer.validated_data['password']):
            return Response({'error': 'نام کاربری یا رمز عبور اشتباه است.'}, status=status.HTTP_401_UNAUTHORIZED)
        verification_code = ''.join(random.choices(string.digits, k=6))
        request.session['verification_code'] = verification_code
        request.session['user_id'] = user.id
        send_mail(
            'ورود به سایت سیم‌کارت',
            f'کد تایید شما: {verification_code}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return Response({
            'message': 'کد تایید به ایمیل شما ارسال شد.'
        }, status=status.HTTP_200_OK)


class LoginVerified(generics.GenericAPIView):
    def post(self, request):
        code = request.data.get('code')
        stored_code = request.session.get('verification_code')
        user_id = request.session.get('user_id')
        if not stored_code or not user_id:
            return Response({'error': 'اطلاعات یا کد تایید یافت نشد.'}, status=status.HTTP_400_BAD_REQUEST)
        if code == stored_code:
            user = get_object_or_404(User, id=user_id)
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            del request.session['verification_code']
            del request.session['user_id']
            return Response({
                'access_token': str(access_token),
                'refresh_token': str(refresh)
            }, status=status.HTTP_200_OK)
        return Response({'error': 'کد وارد شده اشتباه است.'}, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):
        serializer.save()
        return super().perform_update(serializer)


class LogoutView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            logout(request)
            return Response({"message": "شما با موفقیت از سیستم خارج شدید."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "مشکلی در خروج از سیستم رخ داده است."}, status=status.HTTP_400_BAD_REQUEST)


class SimCardListView(generics.ListAPIView):
    serializer_class = SimCardSerializer
    pagination_class = SimCardPagination
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = SimCard.objects.filter(status='published', active=True)
        if self.request.user.is_staff:
            status_param = self.request.query_params.get('status')
            if status_param:
                queryset = SimCard.objects.filter(status=status_param, active=True)
        sim_type_param = self.request.query_params.get('sim_type')
        if sim_type_param:
            queryset = queryset.filter(sim_type=sim_type_param)
        tag_slug = self.request.query_params.get('tag_slug')
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)
        return queryset


class SimCardCreateView(generics.CreateAPIView):
    queryset = SimCard.objects.all()
    serializer_class = SimCardSerializer
    permission_classes = [IsAdminOrReadOnly]

    @transaction.atomic
    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionDenied("شما اجازه‌ی ثبت سیم‌کارت جدید را ندارید.")
        serializer.save()


class SimCardDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SimCard.objects.all()
    serializer_class = SimCardSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_object(self):
        lookup_value = self.kwargs.get("pk")
        lookup_value = str(lookup_value)
        if lookup_value.isdigit():
            return get_object_or_404(SimCard, id=int(lookup_value), active=True)
        return get_object_or_404(SimCard, slug=lookup_value, active=True)

    def retrieve(self, request, *args, **kwargs):
        simcard = self.get_object()
        serializer = self.get_serializer(simcard)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        simcard_id = self.request.query_params.get('simcard_id')
        if simcard_id:
            return Comment.objects.filter(simcard=simcard_id, is_active=True)
        return Comment.objects.filter(status_comment='active')

    @transaction.atomic
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AdminCommentListView(generics.ListAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAdminUser]


class AdminCommentUpdateView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAdminUser]


class AdminCommentDeleteView(generics.DestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAdminUser]

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        simcard_id = self.kwargs['simcard_id']
        comments = Comment.objects.filter(simcard_id=simcard_id)
        count = comments.count()
        comments.delete()
        return Response({'message': f'{count} comment(s) deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)


class ShareSimCardView(generics.RetrieveAPIView):
    queryset = SimCard.objects.all()
    lookup_field = 'pk'

    def retrieve(self, request, *args, **kwargs):
        try:
            simcard = self.get_object()
        except SimCard.DoesNotExist:
            return Response({"error": "SimCard not found"}, status=status.HTTP_404_NOT_FOUND)
        simcard_url = simcard.get_absolute_url()
        share_data = {
            "simcard_title": simcard.title,
            "simcard_url": simcard_url,
            "simcard_number": simcard.number,
            "whatsapp_share_link": generate_whatsapp_link(simcard_url),
            "facebook_share_link": generate_facebook_link(simcard_url),
            "twitter_share_link": generate_twitter_link(simcard_url),
        }
        return Response(share_data, status=status.HTTP_200_OK)


class ContactUs(generics.CreateAPIView):
    permission_classes = []
    serializer_class = ContactSerializer

    def perform_create(self, serializer):
        contact = serializer.save()
        message = contact.message
        username = contact.username
        email = contact.email
        phone = contact.phone
        try:
            send_mail(
                'ارتباط با پشتیبانی از طرف کاربر',
                f'پیام کاربر: {message}\nنام کاربر: {username}\nایمیل: {email}\nشماره همراه کاربر: {phone}',
                settings.DEFAULT_FROM_EMAIL,
                [settings.SUPPORT_EMAIL],
                fail_silently=False,
            )
        except Exception as e:
            raise Exception(f'مشکلی در ارسال پیام پیش آمده است. لطفا دوباره تلاش کنید. خطا: {str(e)}')

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({
            'message': 'پیام شما ارسال شد. لطفا صبور باشید.'
        }, status=status.HTTP_200_OK)


class SearchView(generics.ListAPIView):
    serializer_class = SimCardSerializer
    permission_classes = []
    pagination_class = SimCardPagination

    def get_queryset(self):
        query_name = self.request.GET.get('search_input', None)
        if query_name:
            self.request.session['query_se'] = query_name
        else:
            query_name = self.request.session.get('query_se', "")
        if not query_name:
            if 'query_se' in self.request.session:
                del self.request.session['query_se']
            return SimCard.published.none()
        queryset = SimCard.published.filter(
            Q(title__icontains=query_name) | Q(body__icontains=query_name)
        ).order_by('-created')
        tag_slug = self.kwargs.get('tag_slug', None)
        if tag_slug:
            try:
                tag = Tag.objects.get(slug=tag_slug)
                queryset = queryset.filter(tags__in=[tag])
            except Tag.DoesNotExist:
                pass
        if not queryset.exists():
            search_logger.warning(f"No results found for search: {query_name}")
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"message": f"No results found for '{request.GET.get('search_input', '')}'"},
                            status=status.HTTP_404_NOT_FOUND)
        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(SimCardSerializer(page, many=True).data)
        return Response(SimCardSerializer(queryset, many=True).data, status=status.HTTP_200_OK)
