from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.exceptions import ValidationError
from django.db import transaction


from .models import Categoria, Producto, Item
from .serializers import CategoriaSerializer, ProductoSerializer, ItemSerializer

"""
Para autenticar:
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
"""

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
            productos_data = [ProductoSerializer(producto).data for producto in productos]
            if len(productos_data) == 1:
                categoria_data["producto"]= productos_data[0]
            elif not productos or len(productos_data) == 0: 
                categoria_data["producto"]= "no hay ningun producto todavia"
            else:
                categoria_data["productos"]= productos_data
            return Response({"categoria": categoria_data}, status = status.HTTP_200_OK)
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
            serializer = ProductoSerializer(producto, many = False)
            producto_data = serializer.data
            todos_seriales =  Item.objects.first()
            seriales = Item.objects.filter(producto=producto)
            seriales_data = [ItemSerializer(serial).data for serial in seriales]
            if len(seriales_data) == 1:
                producto_data["serial"]= seriales_data[0]
            elif not seriales or len(seriales_data) == 0:
                producto_data["serial"]= "no hay ningun serial todavia"
            else:
                producto_data["seriales"]= seriales_data

            return Response({"producto": producto_data}, status = status.HTTP_200_OK)
        except Exception as e:
            return Response({"mensaje_de_error": "No existe el producto o no ha podido ser encontrado", "excepcion": str(e)},  status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CrearProducto(APIView):
    @transaction.atomic
    def post(self, request):
        try: 
            data=request.data
            seriales_data = request.data.get("seriales", [])
            serializer = ProductoSerializer(data=data)
            if serializer.is_valid():
                productos = Producto(**serializer.validated_data, categoria  = Categoria.objects.get(id=data["categoria"]))
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
            serializer = ProductoSerializer(producto, data=data)
            if serializer.is_valid():
                serializer.save(categoria = Categoria.objects.get(id=data["categoria"]))
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