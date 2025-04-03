from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth.models import User
from .models import ReporteInteligente
import re

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']
        read_only_fields = fields

class ReporteInteligenteSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)
    resumen = serializers.SerializerMethodField()
    
    class Meta:
        model = ReporteInteligente
        fields = [
            'id',
            'usuario',
            'fecha_creacion',
            'tipo_reporte',
            'resumen',
            'reporte_generado',
            'parametros_modelo',
            'metadata'
        ]
        read_only_fields = fields

    def get_resumen(self, obj):
        return obj.get_resumen()

class GenerarReporteSerializer(serializers.Serializer):
    tipo_reporte = serializers.ChoiceField(
        choices=[
            ('analisis_ventas', 'Análisis de Ventas'),
            ('recomendacion_compras', 'Recomendación de Compras'),
            ('prediccion_inventario', 'Predicción de Inventario')
        ],
        default='analisis_ventas',
        error_messages={
            'required': 'El tipo de reporte es obligatorio',
            'invalid_choice': 'Tipo de reporte no válido. Opciones válidas: analisis_ventas, recomendacion_compras, prediccion_inventario'
        }
    )
    
    fecha_inicio = serializers.DateField(
        required=False,
        error_messages={
            'invalid': 'Formato de fecha inválido. Use YYYY-MM-DD'
        }
    )
    
    fecha_fin = serializers.DateField(
        required=False,
        error_messages={
            'invalid': 'Formato de fecha inválido. Use YYYY-MM-DD'
        }
    )
    
    modelo = serializers.CharField(
        default='deepseek-chat',
        max_length=50,
        error_messages={
            'max_length': 'El nombre del modelo no puede exceder los 50 caracteres'
        }
    )
    
    temperatura = serializers.FloatField(
        default=0.7,
        min_value=0.1,
        max_value=2.0,
        error_messages={
            'min_value': 'La temperatura no puede ser menor que 0.1',
            'max_value': 'La temperatura no puede ser mayor que 2.0'
        }
    )
    
    max_tokens = serializers.IntegerField(
        default=2000,
        min_value=100,
        max_value=4000,
        error_messages={
            'min_value': 'El mínimo de tokens es 100',
            'max_value': 'El máximo de tokens es 4000'
        }
    )

    def validate_modelo(self, value):
        """Valida que el modelo tenga un formato válido"""
        if not re.match(r'^[a-z0-9\-:]+$', value):
            raise serializers.ValidationError("El nombre del modelo solo puede contener letras minúsculas, números, guiones y dos puntos")
        return value.lower()

    def validate_fecha_inicio(self, value):
        """Valida que la fecha de inicio no sea futura"""
        if value and value > timezone.now().date():
            raise serializers.ValidationError("La fecha de inicio no puede ser en el futuro")
        return value
    
    def validate_fecha_fin(self, value):
        """Valida que la fecha fin no sea futura"""
        if value and value > timezone.now().date():
            raise serializers.ValidationError("La fecha fin no puede ser en el futuro")
        return value
    
    def validate(self, data):
        """Validaciones cruzadas entre campos"""
        # Validación de fechas
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        
        if bool(fecha_inicio) != bool(fecha_fin):
            raise serializers.ValidationError({
                'fecha_inicio': 'Debe especificar ambas fechas o ninguna',
                'fecha_fin': 'Debe especificar ambas fechas o ninguna'
            })
        
        if fecha_inicio and fecha_fin:
            if fecha_inicio > fecha_fin:
                raise serializers.ValidationError({
                    'fecha_inicio': 'La fecha de inicio no puede ser mayor que la fecha fin',
                    'fecha_fin': 'La fecha fin no puede ser menor que la fecha de inicio'
                })
            
            # Validar que el rango no sea mayor a 2 años
            if (fecha_fin - fecha_inicio).days > 730:
                raise serializers.ValidationError("El rango de fechas no puede ser mayor a 2 años")
        
        # Validación de parámetros del modelo
        temperatura = data.get('temperatura', 0.7)
        max_tokens = data.get('max_tokens', 2000)
        
        if temperatura > 1.5 and max_tokens > 3000:
            raise serializers.ValidationError(
                "Combinación riesgosa: alta temperatura con muchos tokens. "
                "Recomendación: reduzca temperatura o cantidad de tokens."
            )
        
        return data
    
    def to_internal_value(self, data):
        """Limpia los datos de entrada antes de la validación"""
        # Convertir cadenas vacías a None para campos opcionales
        for field in ['fecha_inicio', 'fecha_fin']:
            if field in data and data[field] == '':
                data[field] = None
        
        # Convertir tipo_reporte a minúsculas si existe
        if 'tipo_reporte' in data and isinstance(data['tipo_reporte'], str):
            data['tipo_reporte'] = data['tipo_reporte'].lower()
        
        return super().to_internal_value(data)