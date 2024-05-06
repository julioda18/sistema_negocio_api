from django.db import models
from rest_framework import serializers
from .models import Categoria, Producto, Item


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ("nombre", "descripcion")

class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = ("nombre", "descripcion", "precio", "cantidad_en_stock", "categoria")

    categoria = CategoriaSerializer(read_only=True)



class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ("numero_serial", "producto")

    producto = ProductoSerializer(read_only=True)
