# wallet/models.py
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from cryptography.fernet import Fernet
import os

ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', Fernet.generate_key())
cipher = Fernet(ENCRYPTION_KEY)


class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wallet")
    balance_toman = models.FloatField(default=0.0, validators=[MinValueValidator(0)])
    balance_trx = models.FloatField(default=0.0, validators=[MinValueValidator(0)])
    trx_address = models.CharField(max_length=34, unique=True, blank=True, null=True)
    encrypted_private_key = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def set_private_key(self, private_key):
        self.encrypted_private_key = cipher.encrypt(private_key.encode()).decode()

    def get_private_key(self):
        if self.encrypted_private_key:
            return cipher.decrypt(self.encrypted_private_key.encode()).decode()
        return None

    def __str__(self):
        return f"کیف پول {self.user.username}"


class Transaction(models.Model):
    TYPE_CHOICES = (
        ('deposit', 'واریز'),
        ('withdrawal', 'برداشت'),
        ('payment', 'پرداخت سبد خرید'),
    )
    CURRENCY_CHOICES = (
        ('toman', 'تومان'),
        ('trx', 'TRX'),
    )
    STATUS_CHOICES = (
        ('pending', 'در انتظار'),
        ('completed', 'تکمیل‌شده'),
        ('failed', 'ناموفق'),
    )
    wallet = models.ForeignKey(Wallet, related_name="transactions", on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    currency = models.CharField(max_length=10, choices=CURRENCY_CHOICES)
    amount = models.FloatField(validators=[MinValueValidator(0)])
    authority = models.CharField(max_length=36, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    tx_hash = models.CharField(max_length=66, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.amount} {self.currency} - {self.status}"
