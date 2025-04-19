# wishlist/views.py
from rest_framework import viewsets, permissions
from .models import Wishlist
from .serializers import WishlistSerializer
from .permissions import IsAdminOrOwner
from django.db import transaction


class WishlistViewSet(viewsets.ModelViewSet):
    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer
    permission_classes = [IsAdminOrOwner]

    def get_queryset(self):
        user = self.request.user
        return Wishlist.objects.filter(user=user)

    @transaction.atomic
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
