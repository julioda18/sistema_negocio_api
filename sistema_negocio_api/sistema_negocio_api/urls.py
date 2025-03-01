"""
URL configuration for sistema_negocio_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class_based views
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
    CrearItem,
    EditarItem,
    BorrarItem,
)

from facturas_y_reportes.views import CrearFactura, VerFacturas, VerFactura

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/clientes/", VerClientes.as_view(), name="clientes"),
    path("api/cliente/<int:id>/", VerCliente.as_view(), name="ver_cliente"),
    path("api/crear_cliente/", CrearCliente.as_view(), name="crear_cliente"),
    path(
        "api/editar_cliente/<int:id>/", EditarCliente.as_view(), name="editar_cliente"
    ),
    path(
        "api/borrar_cliente/<int:id>/", BorrarCliente.as_view(), name="borrar_cliente"
    ),
    path("api/categorias/", VerCategorias.as_view(), name="categorias"),
    path("api/categoria/<int:id>/", VerCategoria.as_view(), name="ver_categoria"),
    path("api/crear_categoria/", CrearCategoria.as_view(), name="crear_categoria"),
    path(
        "api/editar_categoria/<int:id>/",
        EditarCategoria.as_view(),
        name="editar_categoria",
    ),
    path(
        "api/borrar_categoria/<int:id>/",
        BorrarCategoria.as_view(),
        name="borrar_categoria",
    ),
    path("api/productos/", VerProductos.as_view(), name="productos"),
    path("api/producto/<int:id>/", VerProducto.as_view(), name="ver_producto"),
    path("api/crear_producto/", CrearProducto.as_view(), name="crear_producto"),
    path(
        "api/editar_producto/<int:id>/",
        EditarProducto.as_view(),
        name="editar_producto",
    ),
    path(
        "api/borrar_producto/<int:id>/",
        BorrarProducto.as_view(),
        name="borrar_producto",
    ),
    path("api/crear_item/", CrearItem.as_view(), name="crear_item"),
    path("api/editar_item/<int:id>/", EditarItem.as_view(), name="editar_item"),
    path("api/borrar_item/<int:id>/", BorrarItem.as_view(), name="borrar_item"),
    path("api/crear_factura/", CrearFactura.as_view(), name="crear_factura"),
    path("api/facturas/", VerFacturas.as_view(), name="facturas"),
    path("api/factura/<int:factura_id>/", VerFactura.as_view(), name="ver_factura"),
]
