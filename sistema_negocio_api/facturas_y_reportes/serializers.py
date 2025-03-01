from django.db import models
from rest_framework import serializers
from .models import Factura, DetalleFactura
from clientes.models import Cliente
from productos.models import Producto


class FacturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Factura
        fields = ("id", "fecha", "total", "subtotal", "cliente", "metodo_pago")

    cliente = serializers.SlugRelatedField(
        slug_field="id", queryset=Cliente.objects.all()
    )


class DetalleFacturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleFactura
        fields = (
            "cantidad",
            "total_producto",
            "precio_unitario",
            "seriales",
            "factura",
            "producto",
        )

    factura = serializers.SlugRelatedField(
        slug_field="id", queryset=Factura.objects.all()
    )
    producto = serializers.SlugRelatedField(
        slug_field="id", queryset=Producto.objects.all()
    )
