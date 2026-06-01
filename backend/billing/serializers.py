from rest_framework import serializers
from .models import Product, Transaction, ProductPurchase


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "description", "price_cop", "is_active", "created_at"]


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ["id", "amount", "currency", "status", "card_last4", "created_at"]


class ProductPurchaseSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    transaction = TransactionSerializer(read_only=True)

    class Meta:
        model = ProductPurchase
        fields = ["id", "product", "transaction", "purchased_at"]
