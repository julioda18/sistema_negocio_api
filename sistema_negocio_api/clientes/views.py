from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Cliente
from .serializers import ClienteSerializer

"""
Para autenticar:
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
"""

# Create your views here.
class VerClientes(APIView):
    def get(self, request):
        try: 
            clientes = Cliente.objects.all()
            serializer = ClienteSerializer(clientes, many = True)
            return Response({"clientes": serializer.data}, status = status.HTTP_200_OK)
        except Exception as e:
            return Response({"mensaje_de_error": "No existen clientes o no han podido ser encontrados", "excepcion": str(e)},  status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VerCliente(APIView):
    def get(self, request, id):
        try:    
            cliente = Cliente.objects.get(id=id)
            serializer = ClienteSerializer(cliente, many = False)
            return Response({"cliente": serializer.data}, status = status.HTTP_200_OK)
        except Exception as e:
            return Response({"mensaje_de_error": "No existe el cliente o no ha podido ser encontrado", "excepcion": str(e)},  status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CrearCliente(APIView):
    def post(self, request):
        try: 
            serializer = ClienteSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"nuevo_cliente": serializer.data}, status= status.HTTP_201_CREATED)
            else: 
                return Response({"mensaje_de_error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"mensaje_de_error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class EditarCliente(APIView):
    def put(self, request, id):
        try:
            cliente = Cliente.objects.get(id=id)
            serializer = ClienteSerializer(cliente, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"cliente_editado": serializer.data}, status = status.HTTP_200_OK)
            else: 
                return Response({"mensaje_de_error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"mensaje_de_error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BorrarCliente(APIView):
    def delete(self, request, id):
        try:
            cliente = Cliente.objects.get(id=id)
            cliente.delete()
            return Response({"mensaje": "El cliente ha sido borrado correctamente"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"mensaje_de_error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)