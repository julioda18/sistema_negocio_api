from django.db import models
from django.contrib.auth.models import User
from django.core.serializers.json import DjangoJSONEncoder
import json

class ReporteInteligente(models.Model):
    TIPO_REPORTE_CHOICES = [
        ('analisis_ventas', 'Análisis de Ventas'),
        ('recomendacion_compras', 'Recomendación de Compras')
    ]

    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='reportes_generados'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    tipo_reporte = models.CharField(
        max_length=50, 
        choices=TIPO_REPORTE_CHOICES,
        default='analisis_ventas'
    )
    datos_entrada = models.JSONField(
        encoder=DjangoJSONEncoder,
    )
    reporte_generado = models.TextField()
    prompt_utilizado = models.TextField()
    parametros_modelo = models.JSONField(
        default=dict,
        blank=True,
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
    )

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = "Reporte Inteligente"
        verbose_name_plural = "Reportes Inteligentes"
        indexes = [
            models.Index(fields=['usuario', 'fecha_creacion']),
            models.Index(fields=['tipo_reporte']),
        ]

    def __str__(self):
        return f"{self.get_tipo_reporte_display()} - {self.fecha_creacion.strftime('%Y-%m-%d')}"

    def get_resumen(self):
        """Extrae las primeras líneas del reporte como resumen"""
        return self.reporte_generado.split('\n')[0][:100] + '...'