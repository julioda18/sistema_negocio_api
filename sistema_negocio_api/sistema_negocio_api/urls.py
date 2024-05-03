"""
URL configuration for sistema_negocio_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from clientes.views import (
    VerClientes,
    VerCliente,
    CrearCliente,
    EditarCliente,
    BorrarCliente,
)

from productos.views import (
    VerCategorias,
    VerCategoria,
    CrearCategoria,
    EditarCategoria,
    BorrarCategoria,
    VerProductos,
    VerProducto,
    CrearProducto,
    EditarProducto,
    BorrarProducto,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/clientes/', VerClientes.as_view(), name='clientes'),
    path('api/cliente/<int:id>/', VerCliente.as_view(), name='cliente-detail'),
    path('api/crear-cliente/', CrearCliente.as_view(), name='crear-cliente'),
    path('api/editar-cliente/<int:id>/', EditarCliente.as_view(), name='editar-cliente'),
    path('api/borrar-cliente/<int:id>/', BorrarCliente.as_view(), name='borrar-cliente'),
    path('api/categorias/', VerCategorias.as_view(), name='categorias'),
    path('api/categoria/<int:id>/', VerCategoria.as_view(), name='categoria-detail'),
    path('api/crear-categoria/', CrearCategoria.as_view(), name='crear-categoria'),
    path('api/editar-categoria/<int:id>/', EditarCategoria.as_view(), name='editar-categoria'),
    path('api/borrar-categoria/<int:id>/', BorrarCategoria.as_view(), name='borrar-categoria'),
    path('api/productos/', VerProductos.as_view(), name='productos'),
    path('api/producto/<int:id>/', VerProducto.as_view(), name='producto-detail'),
    path('api/crear-producto/', CrearProducto.as_view(), name='crear-producto'),
    path('api/editar-producto/<int:id>/', EditarProducto.as_view(), name='editar-producto'),
    path('api/borrar-producto/<int:id>/', BorrarProducto.as_view(), name='borrar-producto'),
    
]
