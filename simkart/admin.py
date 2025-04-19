# simkart/admin.py

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .models import SimCard, Comment, Account
from django.utils import timezone

User = get_user_model()


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['username', 'email', 'is_active', 'phone_number', 'date_of_birth']
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal Info', {'fields': ('phone_number', 'date_of_birth')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )


class SimCardInline(admin.TabularInline):
    model = SimCard
    extra = 1


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'gender', 'address', 'age', 'created', 'updated', 'active')
    inlines = [SimCardInline]
    search_fields = ('user__username', 'phone_number')
    list_editable = ('active', 'gender')


@admin.register(SimCard)
class SimCardAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'active', 'number', 'price', 'discount', 'status', 'quantity', 'publish', 'created',
        'updated')
    list_filter = ('status', 'sim_type', 'account__user__username', 'publish', 'quantity')
    search_fields = ('title', 'number')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('-publish',)
    list_editable = ('active', 'status')
    list_per_page = 20

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.none()
        return qs

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created = obj.updated = timezone.now()
        super().save_model(request, obj, form, change)

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'simcard', 'created_at', 'updated_at', 'is_active')
    list_filter = ('is_active', 'simcard', 'user')
    search_fields = ('user__username', 'body', 'simcard__title')
    ordering = ('-created_at',)
    list_editable = ('is_active',)
