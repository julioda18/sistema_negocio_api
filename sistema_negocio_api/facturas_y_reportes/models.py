from django.db import models
from clientes.models import Cliente
from productos.models import Producto
from django.db.models import JSONField 

# Create your models here.
class Factura(models.Model):
    METODOS_PAGO = (
        ("banco", "Transferencia/Pago Movil"),
        ("efectivo", "Efectivo"),
        ("pos", "Punto de Venta"),
        ("dolares", "Dolares"),
        ("otro", "Otro"),
    )
    fecha = models.DateField(auto_now_add=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    metodo_pago = models.CharField(choices=METODOS_PAGO, max_length=50)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    total= models.DecimalField(max_digits=12, decimal_places=2)
    
class DetalleFactura(models.Model):
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    total_producto = models.DecimalField(max_digits=12, decimal_places=2)
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    seriales = JSONField(default=list)