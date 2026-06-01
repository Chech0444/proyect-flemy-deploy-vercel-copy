# Generated manually - adds Product, ProductPurchase models and updates Transaction

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("billing", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Product",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("price_cop", models.PositiveIntegerField(help_text="Precio en pesos colombianos (COP)")),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="ProductPurchase",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("purchased_at", models.DateTimeField(auto_now_add=True)),
                ("product", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to="billing.product")),
                (
                    "transaction",
                    models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to="billing.transaction"),
                ),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="product_purchases", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-purchased_at"],
            },
        ),
        migrations.AddField(
            model_name="transaction",
            name="wompi_transaction_id",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AlterField(
            model_name="transaction",
            name="currency",
            field=models.CharField(default="COP", max_length=3),
        ),
        migrations.AlterField(
            model_name="transaction",
            name="card_last4",
            field=models.CharField(blank=True, default="", max_length=4),
        ),
    ]
