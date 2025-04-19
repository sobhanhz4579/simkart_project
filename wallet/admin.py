# wallet/admin.py
from django.contrib import admin
from .models import Wallet, Transaction


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance_toman', 'balance_trx', 'trx_address', 'created_at', 'updated_at')
    search_fields = ('user__username', 'trx_address')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'transaction_type', 'currency', 'amount', 'status', 'created_at', 'updated_at')
    search_fields = ('wallet__user__username', 'transaction_type', 'currency', 'status')
