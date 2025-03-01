from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import Factura, DetalleFactura
from productos.models import Producto, Item
from clientes.models import Cliente
from .serializers import FacturaSerializer, DetalleFacturaSerializer
from decimal import Decimal


class CrearFactura(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def calcular_precio_unitario(self, producto, metodo_pago):
        if metodo_pago == "dolares":
            return producto.precio_dolares / Decimal(1.16)
        return producto.precio_bolivares / Decimal(1.16)

    def dividir_nombre_completo(self, nombre_completo):
        partes_nombre = nombre_completo.strip().split()

        if len(partes_nombre) == 0:
            raise ValueError("El nombre no puede estar vacío")

        if len(partes_nombre) == 1:
            return partes_nombre[0], ""

        if len(partes_nombre) == 2:
            return partes_nombre[0], partes_nombre[1]

        if len(partes_nombre) >= 3:
            nombre = partes_nombre[0]
            apellido = " ".join(partes_nombre[1:])
            return nombre, apellido

    @transaction.atomic
    def post(self, request):
        METODOS_PAGO_VALIDOS = ["dolares", "otro", "banco", "pos", "efectivo"]

        try:
            data = request.data
            cliente_nombre = data.get("cliente")
            metodo_pago = data.get("metodo_pago")
            productos_data = data.get("productos", [])

            if not cliente_nombre:
                return Response(
                    {"mensaje_de_error": "Se requiere el nombre del cliente"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not productos_data:
                return Response(
                    {"mensaje_de_error": "Se requiere al menos un producto"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if metodo_pago not in METODOS_PAGO_VALIDOS:
                return Response(
                    {"mensaje_de_error": "Método de pago no válido"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                nombre, apellido = self.dividir_nombre_completo(cliente_nombre)
                cliente = Cliente.objects.get(
                    nombre__iexact=nombre, apellido__iexact=apellido
                )
            except Cliente.DoesNotExist:
                return Response(
                    {"mensaje_de_error": "El cliente no existe"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            productos = []
            productos_a_actualizar = []
            subtotal = 0
            cantidad_total = 0

            try:
                for producto_data in productos_data:
                    producto_nombre = producto_data.get("nombre")
                    seriales = producto_data.get("seriales", [])

                    producto = Producto.objects.get(nombre=producto_nombre)
                    items = Item.objects.filter(
                        numero_serial__in=seriales, producto=producto
                    )

                    if items.count() < len(seriales):
                        return Response(
                            {
                                "mensaje_de_error": f"Algunos seriales no son válidos o no están asociados al producto {producto_nombre}"
                            },
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                    cantidad = len(seriales)

                    if producto.cantidad_en_stock < cantidad:
                        return Response(
                            {
                                "mensaje_de_error": f"Stock insuficiente para el producto {producto_nombre}"
                            },
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                    precio_unitario = self.calcular_precio_unitario(
                        producto, metodo_pago
                    )
                    total_producto = precio_unitario * cantidad

                    productos.append(
                        {
                            "producto": producto.id,
                            "cantidad": cantidad,
                            "precio_unitario": precio_unitario,
                            "total_producto": total_producto,
                            "seriales": seriales,
                        }
                    )

                    subtotal += total_producto
                    cantidad_total += cantidad

                    producto.cantidad_en_stock -= cantidad
                    productos_a_actualizar.append(producto)

            except Producto.DoesNotExist:
                return Response(
                    {"mensaje_de_error": "el (o los) producto(s) no existe(n)"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            impuesto = subtotal * Decimal(0.16)
            total = subtotal + impuesto
            print(total)

            factura_data = {
                "cliente": cliente.id,
                "metodo_pago": metodo_pago,
                "subtotal": round(subtotal, 2),
                "total": round(total, 2),
            }

            serializer = FacturaSerializer(data=factura_data)
            if serializer.is_valid():
                factura = serializer.save()
            else:
                raise ValidationError(serializer.errors)

            detalles_factura = []
            for producto_data in productos:
                detalle_factura_data = {
                    "factura": factura.id,
                    "producto": producto_data["producto"],
                    "cantidad": producto_data["cantidad"],
                    "precio_unitario": round(producto_data["precio_unitario"], 2),
                    "total_producto": round(producto_data["total_producto"], 2),
                    "seriales": producto_data["seriales"],
                }

                detalle_serializer = DetalleFacturaSerializer(data=detalle_factura_data)
                if detalle_serializer.is_valid():
                    detalle_factura = detalle_serializer.save()
                    detalles_factura.append(detalle_factura)
                else:
                    raise ValidationError(detalle_serializer.errors)

            Producto.objects.bulk_update(productos_a_actualizar, ["cantidad_en_stock"])

            for producto_data in productos_data:
                seriales = producto_data.get("seriales", [])
                items = Item.objects.filter(numero_serial__in=seriales)
                items.delete()

            detalles_factura_serializados = DetalleFacturaSerializer(
                detalles_factura, many=True
            ).data

            return Response(
                {
                    "factura_creada": FacturaSerializer(factura).data,
                    "detalles_factura": detalles_factura_serializados,
                },
                status=status.HTTP_201_CREATED,
            )

        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"mensaje_de_error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class VerFacturas(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        try:
            facturas = Factura.objects.all()
            serializer = FacturaSerializer(facturas, many=True)
            return Response({"facturas": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {
                    "mensaje_de_error": "No existen productos o no han podido ser encontrados",
                    "excepcion": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class VerFactura(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, factura_id):
        try:
            factura = Factura.objects.get(id=factura_id)
            detalles_factura = DetalleFactura.objects.filter(
                factura=factura
            )  # Usar filter, no get

            productos_data = []
            for detalle in detalles_factura:
                producto = detalle.producto
                seriales = detalle.seriales
                productos_data.append(
                    {
                        "nombre": producto.nombre,
                        "cantidad": detalle.cantidad,  # La cantidad está en DetalleFactura
                        "precio_unitario": detalle.precio_unitario,  # Calculado
                        "total_producto": detalle.total_producto,
                        "seriales": seriales,
                    }
                )
            iva = factura.subtotal * Decimal(0.16)
            response_data = {
                "factura": {
                    "id": factura.id,
                    "cliente": f"{factura.cliente.nombre} {factura.cliente.apellido}",
                    "metodo_pago": factura.metodo_pago,
                    "subtotal": factura.subtotal,
                    "IVA": round(iva, 2),
                    "total": factura.total,
                    "fecha_creacion": factura.fecha,
                },
                "detalles_factura": productos_data,  # Lista de productos con sus detalles
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Factura.DoesNotExist:
            return Response(
                {"mensaje_de_error": "La factura no existe"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"mensaje_de_error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
