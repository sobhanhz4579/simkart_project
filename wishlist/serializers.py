# wishlist/serializers.py
from rest_framework import serializers
from .models import Wishlist
from simkart.serializers import SimCardSerializer


class WishlistSerializer(serializers.ModelSerializer):
    simcard = SimCardSerializer(read_only=True)

    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'simcard', 'created', 'updated']
        read_only_fields = ['user', 'created', 'updated']

    def validate(self, data):
        user = self.context['request'].user
        if Wishlist.objects.filter(user=user, simcard=data['simcard']).exists():
            raise serializers.ValidationError("این سیم‌کارت قبلاً در لیست علاقه‌مندی‌های شما وجود دارد.")
        return data
