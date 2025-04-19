# cart/signals.py
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from .models import Cart, CartItem, Invoice


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_Cart(sender, instance, created, **kwargs):
    if created:
        Cart.objects.create(user=instance)


@receiver(pre_save, sender=Cart)
def set_cart_dates(sender, instance, **kwargs):
    if not instance.pk:
        instance.created_at = instance.created_at or timezone.now()
    instance.updated_at = timezone.now()


@receiver(post_save, sender=CartItem)
def send_cart_item_notification(sender, instance, created, **kwargs):
    if created and instance.cart.status == 'pending':
        user_email = instance.cart.user.email
        send_mail(
            'آیتم جدید در سبد خرید شما',
            f'آیتم جدیدی به سبد خرید شما اضافه شد: {instance.simcard.title}.',
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False,
        )


@receiver(post_save, sender=Cart)
def create_invoice_for_completed_cart(sender, instance, created, **kwargs):
    if instance.status == 'completed' and not created:
        if not Invoice.objects.filter(cart=instance).exists():
            Invoice.objects.create(cart=instance, amount=instance.total_price())
