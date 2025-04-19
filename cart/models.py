# cart/models.py
from django.db import models
from django.conf import settings
from simkart.models import SimCard


class Cart(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def total_price(self):
        return sum(item.get_total_price() for item in self.items.all())

    def __str__(self):
        return f"سبد خرید {self.user.username} - وضعیت: {self.status}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name="items", on_delete=models.CASCADE)
    simcard = models.ForeignKey(SimCard, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def get_total_price(self):
        discounted_price = self.simcard.price - (self.simcard.price * self.simcard.discount / 100)
        return self.quantity * discounted_price

    def __str__(self):
        return f"{self.quantity} x {self.simcard.title}"


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.city}, {self.country}"


class Invoice(models.Model):
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice for Cart {self.cart.id} - Amount: {self.amount}"
