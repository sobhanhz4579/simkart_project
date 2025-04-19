# wallet/signals.py
from tronpy import Tron
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Wallet, Transaction


@receiver(pre_save, sender=Wallet)
def set_wallet_dates(sender, instance, **kwargs):
    if not instance.pk:
        instance.created_at = instance.created_at or timezone.now()
    instance.updated_at = timezone.now()


@receiver(post_save, sender=User)
def create_wallet(sender, instance, created, **kwargs):
    if created:
        tron = Tron()
        account = tron.generate_address()
        wallet = Wallet.objects.create(
            user=instance,
            trx_address=account['base58check_address']
        )
        wallet.set_private_key(account['private_key'])
        wallet.save()


@receiver(post_save, sender=Transaction)
def send_transaction_notification(sender, instance, created, **kwargs):
    if instance.status == 'completed' and not created:
        user_email = instance.wallet.user.email
        send_mail(
            'تراکنش موفق',
            f'تراکنش {instance.transaction_type} به مبلغ {instance.amount} {instance.currency} با موفقیت انجام شد.',
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False,
        )
