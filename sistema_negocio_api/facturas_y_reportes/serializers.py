from django.db import models
from rest_framework import serializers
from .models import Factura, DetalleFactura
from clientes.serializers import ClienteSerializer
from productos.serializers import ProductoSerializer


class FacturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Factura
        fields = ("nombre", "fecha", "total", "cliente")
    
    cliente = ClienteSerializer(read_only=True)

class DetalleFacturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleFactura
        fields = ("nombre", "descripcion", "cantidad", "subtotal", "cantidad", "factura", "producto")
    
    factura = FacturaSerializer(read_only=True)
    producto = ProductoSerializer(read_only=True)