# Generated by Django 5.0.4 on 2025-02-21 18:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("facturas_y_reportes", "0002_remove_factura_nombre_alter_factura_metodo_pago"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="detallefactura",
            name="precio_producto",
        ),
    ]
