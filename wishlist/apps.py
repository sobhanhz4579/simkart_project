# wishlist/apps.py
from django.apps import AppConfig


class WishlistConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'wishlist'
    verbose_name = 'Wishlist'

    def ready(self):
        import wishlist.signals
