from django.contrib import admin
from .models import Product, Transaction, ProductPurchase


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "price_cop", "is_active", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["name"]


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ["user", "amount", "currency", "status", "created_at"]
    list_filter = ["status", "currency"]
    search_fields = ["user__email", "user__username"]


@admin.register(ProductPurchase)
class ProductPurchaseAdmin(admin.ModelAdmin):
    list_display = ["user", "product", "purchased_at"]
    list_filter = ["purchased_at"]
    search_fields = ["user__email", "product__name"]
