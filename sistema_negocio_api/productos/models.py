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
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)