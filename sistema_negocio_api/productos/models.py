from django.db import models

# Create your models here.
class Categoria(models.Model):
    nombre= models.CharField(max_length=200)
    descripcion= models.TextField()

class Producto(models.Model):
    nombre= models.CharField(max_length=200)
    descripcion= models.TextField()
    precio_dolares= models.DecimalField(max_digits=12, decimal_places=2)
    precio_bolivares= models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cantidad_en_stock = models.IntegerField(default=0)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)

class Item(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    numero_serial = models.CharField(max_length=30, unique=True)
