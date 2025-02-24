from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import Factura, DetalleFactura
from productos.models import Producto
from clientes.models import Cliente
from .serializers import FacturaSerializer, DetalleFacturaSerializer

class CrearFactura(APIView):
    def calcular_precio_unitario(self, producto, metodo_pago):
        if metodo_pago == "dolares":
            return producto.precio_dolares / 1.16
        return producto.precio_bolivares / 1.16
    @transaction.atomic
    def post(self, request):
        METODOS_PAGO_VALIDOS = ["dolares", "otro", "banco", "pos", "efectivo"]

        try:
            data = request.data
            cliente_nombre = data.get("cliente")
            metodo_pago = data.get("metodo_pago")
            productos_data = data.get("productos", [])
        
            if not cliente_nombre:
                return Response({"mensaje_de_error": "Se requiere el nombre del cliente"}, status=status.HTTP_400_BAD_REQUEST)

            if not productos_data:
                return Response({"mensaje_de_error": "Se requiere al menos un producto"}, status=status.HTTP_400_BAD_REQUEST)
            
            if metodo_pago not in METODOS_PAGO_VALIDOS:
                return Response({"mensaje_de_error": "Método de pago no válido"}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                cliente = Cliente.objects.get(nombre=cliente_nombre)
            except Cliente.DoesNotExist:
                return Response({"mensaje_de_error": "El cliente no existe"}, status=status.HTTP_404_NOT_FOUND)
            
            productos = []
            productos_a_actualizar = []
            subtotal = 0
            cantidad_total = 0

            try:
                for producto_data in productos_data:
                    producto_nombre = producto_data.get("nombre")
                    cantidad = producto_data.get("cantidad", 1)
                    producto = Producto.objects.get(nombre=producto_nombre)

                    if producto.cantidad_en_stock < cantidad:
                        return Response({"mensaje_de_error": f"Stock insuficiente para el producto {producto_nombre}"}, status=status.HTTP_400_BAD_REQUEST)
            
                    precio_unitario = self.calcular_precio_unitario(producto, metodo_pago)    
                    total_producto = precio_unitario * cantidad

                    productos.append({
                        "nombre": producto.nombre,
                        "cantidad": cantidad,
                        "precio_unitario" : precio_unitario,
                        "total_producto": total_producto    
                    })

                    subtotal += total_producto
                    cantidad_total += cantidad

                    producto.cantidad_en_stock -= cantidad
                    productos_a_actualizar.append(producto)

            except Producto.DoesNotExist:
                return Response({"mensaje_de_error": "el (o los) producto(s) no existe(n)"}, status=status.HTTP_404_NOT_FOUND)
    
            impuesto = subtotal * 0.16
            total = subtotal + impuesto
            
            factura_data ={
                "cliente": cliente.id,
                "metodo_pago": metodo_pago,
                "total": total
            }
            serializer = FacturaSerializer(data=factura_data)
            if serializer.is_valid():
                factura = serializer.save()
            else: 
                raise ValidationError(serializer.errors)
            
            detalle_factura_data = {
                    "factura": factura.id,
                    "subtotal": subtotal,
                    "cantidad": cantidad_total,
                    "productos": productos,
                }
            detalle_serializer = DetalleFacturaSerializer(data=detalle_factura_data)

            if detalle_serializer.is_valid():
                detalle_factura = detalle_serializer.save()
            else:
                raise ValidationError(detalle_serializer.errors)
            
            Producto.objects.bulk_update(productos_a_actualizar, ["cantidad_en_stock"])
        
            return Response({"factura_creada": FacturaSerializer(factura).data,
                             "detalle_factura": DetalleFacturaSerializer(detalle_factura).data}, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"mensaje_de_error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class VerFacturas(APIView):
    def get(self, request):
        try: 
            facturas = Factura.objects.all()
            serializer = FacturaSerializer(facturas, many = True)
            return Response({"facturas": serializer.data}, status = status.HTTP_200_OK)
        except Exception as e:
            return Response({"mensaje_de_error": "No existen productos o no han podido ser encontrados", "excepcion": str(e)},  status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class VerFactura(APIView):
    def get(self, request, factura_id):
        try:
            factura = Factura.objects.get(id=factura_id)
            detalle_factura = DetalleFactura.objects.get(factura=factura)
            
            productos = detalle_factura.producto.all() 
            
            # Construir la lista de productos
            productos_data = []
            for producto in productos:
                productos_data.append({
                    "nombre": producto.nombre,
                    "cantidad": producto.cantidad,  # Asume que la cantidad está en el modelo Producto
                    "precio_unitario": producto.precio_unitario,
                    "total_producto": producto.cantidad * producto.precio_unitario
                })

            response_data = {
                "factura": {
                    "id": factura.id,
                    "cliente": factura.cliente.nombre,
                    "metodo_pago": factura.metodo_pago,
                    "total": factura.total, 
                    "fecha_creacion": factura.fecha
                },
                "detalle_factura": {
                    "id": detalle_factura.id,
                    "subtotal": detalle_factura.subtotal,
                    "cantidad": detalle_factura.cantidad,
                    "productos": detalle_factura.producto
                }
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Factura.DoesNotExist:
            return Response({"mensaje_de_error": "La factura no existe"}, status=status.HTTP_404_NOT_FOUND)
        except DetalleFactura.DoesNotExist:
            return Response({"mensaje_de_error": "El detalle de la factura no existe"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"mensaje_de_error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)