from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import Categoria, Producto, Item
from .serializers import CategoriaSerializer, ProductoSerializer, ItemSerializer
from pyDolarVenezuela.pages import AlCambio
from pyDolarVenezuela import Monitor
from decimal import Decimal

"""
Para autenticar:
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
"""

def obtener_precio_dolar():
    try:
        monitor = Monitor(AlCambio, 'USD')
        bcv = monitor.get_value_monitors("bcv")
        if bcv is None:
            raise ValueError("No se pudo obtener el valor del dólar desde el monitor.")
        precio_dolar = bcv.price
        return precio_dolar
    except Exception as e:
        print(f'Error al obtener el precio del dólar: {e}')
        return None


class VerCategorias(APIView):
    def get(self, request):
        try: 
            categorias = Categoria.objects.all()
            serializer = CategoriaSerializer(categorias, many = True)
            return Response({"categorias": serializer.data}, status = status.HTTP_200_OK)
        except Exception as e:
            return Response({"mensaje_de_error": "No existen categorias o no han podido ser encontradas", "excepcion": str(e)},  status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VerCategoria(APIView):
    def get(self, request, id):
        try:    
            categoria = Categoria.objects.get(id=id)
            serializer = CategoriaSerializer(categoria, many = False)
            productos = Producto.objects.filter(categoria=categoria)
            categoria_data = serializer.data
            productos_data = ProductoSerializer(productos, many=True).data
            
            if not productos or len(productos_data) == 0: 
                categoria_data["productos"]= "no hay ningun producto todavia"
            else:
                categoria_data["productos"]= productos_data
            return Response({"categoria": categoria_data}, status = status.HTTP_200_OK)
        except Categoria.DoesNotExist:
            return Response({"mensaje_de_error": "El producto no existe"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"mensaje_de_error": "No existe la categoria o no ha podido ser encontrada", "excepcion": str(e)},  status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CrearCategoria(APIView):
    def post(self, request):
        try: 
            serializer = CategoriaSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"nueva_categoria": serializer.data}, status= status.HTTP_201_CREATED)
            else: 
                return Response({"mensaje_de_error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"mensaje_de_error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class EditarCategoria(APIView):
    def put(self, request, id):
        try:
            categoria = Categoria.objects.get(id=id)
            serializer = CategoriaSerializer(categoria, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"categoria_editada": serializer.data}, status = status.HTTP_200_OK)
            else: 
                return Response({"mensaje_de_error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"mensaje_de_error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BorrarCategoria(APIView):
    def delete(self, request, id):
        try:
            categoria = Categoria.objects.get(id=id)
            categoria.delete()
            return Response({"mensaje": "La categoria ha sido borrada correctamente"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"mensaje_de_error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VerProductos(APIView):
    def get(self, request):
        try: 
            productos = Producto.objects.all()
            serializer = ProductoSerializer(productos, many = True)
            return Response({"productos": serializer.data}, status = status.HTTP_200_OK)
        except Exception as e:
            return Response({"mensaje_de_error": "No existen productos o no han podido ser encontrados", "excepcion": str(e)},  status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VerProducto(APIView):
    def get(self, request, id):
        try:
            producto = Producto.objects.get(id=id)
            producto_data = ProductoSerializer(producto).data
            seriales = Item.objects.filter(producto=producto)
            seriales_data = ItemSerializer(seriales, many=True).data

            if seriales_data:
                producto_data["seriales"] = seriales_data
            else:
                producto_data["seriales"] = "No hay ningún serial todavía"
            return Response({"producto": producto_data}, status=status.HTTP_200_OK)

        except Producto.DoesNotExist:
            return Response({"mensaje_de_error": "El producto no existe"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"mensaje_de_error": "Ha ocurrido un error al procesar la solicitud", "excepcion": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CrearProducto(APIView):
    @transaction.atomic
    def post(self, request):
        try: 
            data=request.data
            seriales_data = request.data.get("seriales", [])
            categoria = Categoria.objects.get(nombre=data["categoria"])
            serializer = ProductoSerializer(data=data)
            if serializer.is_valid():
                productos = Producto(**serializer.validated_data, categoria  = categoria)
                productos.save()
            else: 
                raise ValidationError(serializer.errors)
            seriales = []
            for serial_data in seriales_data:
                seriales_serializer = ItemSerializer(data=serial_data)
                if seriales_serializer.is_valid():
                    serial = Item(**seriales_serializer.validated_data, producto=productos)
                    serial.save()
                    seriales.append(serial)
                else: 
                    raise ValidationError(seriales_serializer.errors)
            
            productos.cantidad_en_stock = len(seriales)
            precio_dolar = obtener_precio_dolar()
            if precio_dolar is not None:
                productos.precio_bolivares = productos.precio_dolares * Decimal(precio_dolar)
            productos.save()

            return Response({"nuevo_producto": ProductoSerializer(productos).data, 
                             "seriales": [ItemSerializer(serial).data for serial in seriales],
                             }, status= status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"mensaje_de_error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class EditarProducto(APIView):
    def put(self, request, id):
        try:
            data=request.data
            producto = Producto.objects.get(id=id)
            categoria = Categoria.objects.get(nombre=data["categoria"])
            serializer = ProductoSerializer(producto, data=data)
            if serializer.is_valid():
                serializer.save(categoria = categoria)
                precio_dolar = obtener_precio_dolar()
                if precio_dolar is not None:
                    producto.precio_bolivares = producto.precio_dolares * Decimal(precio_dolar)
                    producto.save()
                return Response({"producto_editado": serializer.data}, status = status.HTTP_200_OK)
            else: 
                return Response({"mensaje_de_error": serializer.errors}, status = status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"mensaje_de_error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BorrarProducto(APIView):
    def delete(self, request, id):
        try:
            producto = Producto.objects.get(id=id)
            producto.delete()
            return Response({"mensaje": "El producto ha sido borrado correctamente"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"mensaje_de_error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CrearItem(APIView):
    def post(self, request):
        try:
            data = request.data
            producto_nombre = data.get("producto")
            serializer = ItemSerializer(data=data)
            if not producto_nombre:
                return Response({"mensaje_de_error": "Se requiere el nombre del producto"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                producto = Producto.objects.get(nombre=producto_nombre)
            except Producto.DoesNotExist:
                return Response({"mensaje_de_error": "El producto no existe"}, status=status.HTTP_404_NOT_FOUND)

            if serializer.is_valid():
                item = Item(**serializer.validated_data, producto=producto)
                item.save()
                producto.cantidad_en_stock += 1
                producto.save()
            else: 
                raise ValidationError(serializer.errors)
            
            return Response({"item_creado": ItemSerializer(item).data}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"mensaje_de_error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class EditarItem(APIView):
    def put(self, request, id):
        try:
            data = request.data
            item = Item.objects.get(id=id)
            serializer = ItemSerializer(item, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"item_editado": serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({"mensaje_de_error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Item.DoesNotExist:
            return Response({"mensaje_de_error": "El serial no existe"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"mensaje_de_error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BorrarItem(APIView):
    def delete(self, request, id):
        try:
            item = Item.objects.get(id=id)
            producto = item.producto  
            item.delete()
            if producto.cantidad_en_stock > 0:
                producto.cantidad_en_stock -= 1
                producto.save()
            else:
                return Response({"mensaje_de_error": "El stock ya es 0, no se puede reducir más"}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"mensaje": "El Item ha sido borrado correctamente y el stock se ha reducido"}, status=status.HTTP_204_NO_CONTENT)

        except Item.DoesNotExist:
            return Response({"mensaje_de_error": "El Item no existe"}, status=status.HTTP_404_NOT_FOUND)

        except Producto.DoesNotExist:
            return Response({"mensaje_de_error": "El Producto asociado no existe"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"mensaje_de_error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)