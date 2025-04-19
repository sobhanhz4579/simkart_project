# wishlist/models.py
from django.db import models
from django.conf import settings
from simkart.models import SimCard


class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='wishlist', on_delete=models.CASCADE)
    simcard = models.ForeignKey(SimCard, related_name='wishlists', on_delete=models.CASCADE, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'simcard']

    def __str__(self):
        return f"{self.user.username}'s Wishlist"
