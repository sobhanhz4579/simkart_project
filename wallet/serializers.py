# wallet/serializers.py
from rest_framework import serializers
from .models import Wallet, Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'transaction_type', 'currency', 'amount', 'description', 'status', 'tx_hash', 'created_at',
                  'updated_at']


class WalletSerializer(serializers.ModelSerializer):
    transactions = TransactionSerializer(many=True, read_only=True)

    class Meta:
        model = Wallet
        fields = ['id', 'user', 'balance_toman', 'balance_trx', 'trx_address', 'transactions', 'created_at',
                  'updated_at']
