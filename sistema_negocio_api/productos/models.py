from django.db import models

# Create your models here.
class Categoria(models.Model):
    nombre= models.CharField(max_length=200)
    descripcion= models.TextField()

class Producto(models.Model):
    nombre= models.CharField(max_length=200)
    descripcion= models.TextField()
    precio= models.FloatField()
    cantidad_en_stock = models.IntegerField()
    numero_serial = models.CharField(max_length=30, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)

"""
class Item(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    numero_serial = models.CharField(max_length=30)
"""