from pyDolarVenezuela.pages import AlCambio
from pyDolarVenezuela import Monitor
from .models import Producto

def obtener_precio_dolar():
    try:
        monitor = Monitor(AlCambio, 'USD')
        bcv = monitor.get_value_monitors("bcv")
        if bcv is None:
            raise ValueError("No se pudo obtener el valor del dólar desde el monitor.")
        precio_dolar = bcv.price
        return precio_dolar
    except Exception as e:
        # Captura cualquier excepción que ocurra durante la obtención del precio
        print(f"Error al obtener el precio del dólar: {e}")
        return None  # Retorna None en caso de error

def actualizar_precios():
    try:
        productos = Producto.objects.all()
        precio_bolivares = obtener_precio_dolar()

        if precio_bolivares is None:
            raise ValueError("No se pudo obtener el precio del dólar. No se actualizarán los precios.")

        for producto in productos:
            try:
                nuevo_precio = producto.precio_dolares * precio_bolivares
                producto.precio_bolivares = nuevo_precio
                producto.save()
            except Exception as e:
                # Captura errores al actualizar un producto específico
                print(f"Error al actualizar el producto {producto.id}: {e}")
                continue  # Continúa con el siguiente producto si hay un error

    except Exception as e:
        # Captura errores generales en la función
        print(f"Error en la función actualizar_precios: {e}")

def run():
    print(obtener_precio_dolar())