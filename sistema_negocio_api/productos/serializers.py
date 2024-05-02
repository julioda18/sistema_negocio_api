from django.db import models
from rest_framework import serializers
from .models import Categoria, Producto


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ("nombre", "descripcion")

class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = ("nombre", "precio_unitario", "precio", "cantidad_en_stock", "numero_serial", "categoria")
    
    categoria = CategoriaSerializer(read_only=True)