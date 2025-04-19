# simkart/apps.py
from django.apps import AppConfig


class SimkartConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'simkart'

    def ready(self):
        import simkart.signals
