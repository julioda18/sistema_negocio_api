from django.db import models
from clientes.models import Cliente
from productos.models import Producto

# Create your models here.
class Factura(models.Model):
    nombre= models.CharField(max_length=200)
    fecha = models.DateField(auto_now_add=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    total= models.FloatField()

class DetalleFactura(models.Model):
    nombre= models.CharField(max_length=200)
    precio_unitario= models.FloatField()
    cantidad = models.IntegerField()
    subtotal= models.FloatField()
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)