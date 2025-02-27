from django.core.management.base import BaseCommand
from pyDolarVenezuela.pages import AlCambio
from pyDolarVenezuela import Monitor
from productos.models import Producto  # Ajusta la importación según tu estructura
from decimal import Decimal

class Command(BaseCommand):
    help = 'Actualiza los precios de los productos en bolívares según el precio del dólar.'

    def handle(self, *args, **kwargs):
        precio_dolar = self.obtener_precio_dolar()

        if precio_dolar is None:
            self.stdout.write(self.style.ERROR('No se pudo obtener el precio del dólar. No se actualizarán los precios.'))
            return

        self.actualizar_precios(precio_dolar)

    def obtener_precio_dolar(self):
        try:
            monitor = Monitor(AlCambio, 'USD')
            bcv = monitor.get_value_monitors("bcv")
            if bcv is None:
                raise ValueError("No se pudo obtener el valor del dólar desde el monitor.")
            precio_dolar = bcv.price
            return precio_dolar
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error al obtener el precio del dólar: {e}'))
            return None

    def actualizar_precios(self, precio_bolivares):
        try:
            productos = Producto.objects.all()
            for producto in productos:
                try:
                    nuevo_precio = producto.precio_dolares * Decimal(precio_bolivares)
                    producto.precio_bolivares = nuevo_precio
                    producto.save()
                    self.stdout.write(self.style.SUCCESS(f'Precio actualizado para el producto {producto.id}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error al actualizar el producto {producto.id}: {e}'))
                    continue
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error en la función actualizar_precios: {e}'))