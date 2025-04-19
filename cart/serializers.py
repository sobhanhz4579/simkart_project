# cart/serializers.py
from rest_framework import serializers
from .models import Cart, CartItem, Address, Invoice
from simkart.serializers import SimCardSerializer


class CartItemSerializer(serializers.ModelSerializer):
    simcard = SimCardSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'simcard', 'quantity']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'status', 'created_at', 'updated_at']


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['street', 'city', 'postal_code', 'country']


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = '__all__'
