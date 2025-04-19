# wishlist/admin.py
from django.contrib import admin
from .models import Wishlist


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'simcard', 'created', 'updated']
    list_filter = ['user']
    search_fields = ['user__username', 'simcard__title']
