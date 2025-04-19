# cart/admin.py
from django.contrib import admin
from .models import Cart, CartItem, Address, Invoice


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'created_at', 'updated_at')
    search_fields = ('user__username', 'status')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'simcard', 'quantity')
    search_fields = ('simcard__title',)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'street', 'city', 'postal_code', 'country', 'created', 'updated')
    search_fields = ('user__username', 'street', 'city', 'postal_code', 'country')


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('cart', 'amount', 'created')
    search_fields = ('cart__id', 'amount')
