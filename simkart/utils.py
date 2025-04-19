# simkart/utils.py
from django.core.mail import send_mail
from django.conf import settings
import urllib.parse


def send_share_email(to_email, simcard_url):
    subject = "Check out this SimCard!"
    message = f"Here's a great SimCard: {simcard_url}"
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [to_email], fail_silently=False)


def generate_whatsapp_link(simcard_url):
    base_url = "https://wa.me/?text="
    message = f"Check out this SimCard: {simcard_url}"
    return base_url + urllib.parse.quote(message)


def generate_facebook_link(simcard_url):
    base_url = "https://www.facebook.com/sharer/sharer.php?u="
    return base_url + urllib.parse.quote(simcard_url)


def generate_twitter_link(simcard_url):
    base_url = "https://twitter.com/intent/tweet?url="
    return base_url + urllib.parse.quote(simcard_url)
