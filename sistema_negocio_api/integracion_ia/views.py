from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Q
from datetime import datetime, timedelta
import json

from .models import ReporteInteligente
from facturas_y_reportes.models import DetalleFactura, Factura
from productos.models import Producto
from .serializers import ReporteInteligenteSerializer, GenerarReporteSerializer
from .deepseek_service import DeepSeekService

class ListarReportesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        reportes = ReporteInteligente.objects.filter(usuario=request.user)
        
        # Filtros
        tipo_reporte = request.query_params.get('tipo')
        if tipo_reporte:
            reportes = reportes.filter(tipo_reporte=tipo_reporte)
        
        # Búsqueda
        busqueda = request.query_params.get('q')
        if busqueda:
            reportes = reportes.filter(
                Q(reporte_generado__icontains=busqueda) |
                Q(prompt_utilizado__icontains=busqueda)
            )
        
        serializer = ReporteInteligenteSerializer(reportes.order_by('-fecha_creacion'), many=True)
        return Response(serializer.data)

class CrearReporteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = GenerarReporteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Obtener datos de facturación
        datos_ventas = self._obtener_datos_ventas(
            request.user,
            serializer.validated_data.get('fecha_inicio'),
            serializer.validated_data.get('fecha_fin')
        )
        
        # Generar prompt
        prompt = self._generar_prompt(
            datos_ventas,
            serializer.validated_data['tipo_reporte']
        )
        
        # Generar reporte con DeepSeek
        deepseek = DeepSeekService(
            model=serializer.validated_data.get('modelo', 'deepseek-chat'),
            temperature=serializer.validated_data.get('temperatura', 0.7),
            max_tokens=serializer.validated_data.get('max_tokens', 2000)
        )
        
        reporte_generado = deepseek.generate_report(prompt)
        
        # Guardar reporte
        reporte = ReporteInteligente.objects.create(
            usuario=request.user,
            tipo_reporte=serializer.validated_data['tipo_reporte'],
            datos_entrada=datos_ventas,
            reporte_generado=reporte_generado,
            prompt_utilizado=prompt,
            parametros_modelo={
                'modelo': serializer.validated_data.get('modelo', 'deepseek-chat'),
                'temperatura': serializer.validated_data.get('temperatura', 0.7),
                'max_tokens': serializer.validated_data.get('max_tokens', 2000)
            }
        )
        
        return Response(
            ReporteInteligenteSerializer(reporte).data,
            status=status.HTTP_201_CREATED
        )

    def _obtener_datos_ventas(self, user, fecha_inicio=None, fecha_fin=None):
        facturas = Factura.objects.all()
        
        if fecha_inicio and fecha_fin:
            facturas = facturas.filter(
                fecha__date__gte=fecha_inicio,
                fecha__date__lte=fecha_fin
            )
        else:
            facturas = facturas.filter(
                fecha__date__gte=datetime.now() - timedelta(days=30)
            )
        
        detalles = DetalleFactura.objects.filter(factura__in=facturas)
        productos_vendidos = Producto.objects.filter(
            id__in=detalles.values_list('producto_id', flat=True)
        )
        
        return {
            'periodo': {
                'inicio': fecha_inicio.isoformat() if fecha_inicio else None,
                'fin': fecha_fin.isoformat() if fecha_fin else None
            },
            'total_facturas': facturas.count(),
            'productos_mas_vendidos': [
                {
                    'nombre': p.nombre,
                    'cantidad_vendida': detalles.filter(producto=p).aggregate(Sum('cantidad'))['cantidad__sum'] or 0
                }
                for p in productos_vendidos
            ]
        }

    def _generar_prompt(self, datos, tipo_reporte):
        plantillas = {
            'ANALISIS_VENTAS': """
                Analiza estos datos de ventas:
                {datos}
                
                Proporciona:
                1. Tendencias clave
                2. Productos destacados
                3. Recomendaciones estratégicas
            """,
            'RECOMENDACION_COMPRAS': """
                Con estos datos:
                {datos}
                
                Genera recomendaciones de compra:
                1. Productos a reponer
                2. Cantidades sugeridas
                3. Prioridades
            """
        }
        return plantillas.get(tipo_reporte, plantillas['ANALISIS_VENTAS']).format(
            datos=json.dumps(datos, indent=2)
        )

class DetalleReporteView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        reporte = get_object_or_404(
            ReporteInteligente,
            pk=pk,
            usuario=request.user
        )
        serializer = ReporteInteligenteSerializer(reporte)
        return Response(serializer.data)

class BorrarReporteView(APIView):
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, pk):
        reporte = get_object_or_404(
            ReporteInteligente,
            pk=pk,
            usuario=request.user
        )
        reporte.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)












