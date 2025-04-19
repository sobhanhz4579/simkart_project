# simkart/models.py

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from django.utils.text import slugify
from taggit.managers import TaggableManager


class Account(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    last_login = models.DateTimeField(auto_now=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    address = models.TextField(blank=True, null=True, default="")
    age = models.IntegerField(null=True, blank=True, default=18)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status='published', active=True)


class SimCard(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published')
    )
    SIM_TYPE_CHOICES = [
        ('prepaid', 'Prepaid'),
        ('postpaid', 'Postpaid'),
    ]
    title = models.CharField(max_length=255)
    account = models.ForeignKey('Account', related_name='simcards', on_delete=models.CASCADE)
    body = models.TextField()
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    number = models.CharField(max_length=15, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    publish = models.DateTimeField(default=timezone.now)
    sim_type = models.CharField(max_length=20, choices=SIM_TYPE_CHOICES, default='prepaid')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    quantity = models.IntegerField(default=1)
    tags = TaggableManager()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    objects = models.Manager()
    published = PublishedManager()

    def get_absolute_url(self):
        return reverse('simkart:simcard-detail', args=[self.pk])

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while SimCard.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Comment(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('no_active', 'not_Active')
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments_user')
    simcard = models.ForeignKey(SimCard, related_name='comments', on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status_comment = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_active = models.BooleanField(default=True)
    objects = models.Manager()

    def __str__(self):
        return f"Comment by {self.user.username} on {self.simcard.title}"


class ContactModel(models.Model):
    username = models.CharField(max_length=250, blank=False)
    email = models.EmailField(blank=False)
    message = models.TextField(blank=False)
    phone = models.CharField(max_length=15, blank=False)
