# wishlist/signals.py
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Wishlist
from django.utils.timezone import now
from django.conf import settings


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_Wishlist(sender, instance, created, **kwargs):
    if created:
        Wishlist.objects.create(user=instance)


@receiver(pre_save, sender=Wishlist)
def set_wishlist_dates(sender, instance, **kwargs):
    if not instance.pk:
        instance.created = now()
    instance.updated = now()
