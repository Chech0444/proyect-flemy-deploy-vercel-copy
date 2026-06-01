from django.db import migrations


def seed_test_product(apps, schema_editor):
    Product = apps.get_model("billing", "Product")
    Product.objects.get_or_create(
        name="Crédito de Prueba 500 COP",
        price_cop=500,
        defaults={
            "description": "Producto de prueba para verificar el flujo de pago. Válido por 24 horas.",
            "is_active": True,
        },
    )


def reverse_seed(apps, schema_editor):
    Product = apps.get_model("billing", "Product")
    Product.objects.filter(name="Crédito de Prueba 500 COP", price_cop=500).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("billing", "0002_product_productpurchase_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_test_product, reverse_seed),
    ]
