from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from unittest.mock import patch
from datetime import datetime, timedelta
from decimal import Decimal
import json

class TestCrearReporteEstaticoView(TestCase):
    def setUp(self):
        # Usuario de prueba (requerido por IsAuthenticated)
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # ------------------------------------------
        # DATOS ESTÁTICOS EN MEMORIA (sin BD)
        # ------------------------------------------
        self.datos_estaticos = {
            'clientes': [
                {
                    'id': 1,
                    'nombre': 'Juan',
                    'apellido': 'Pérez',
                    'correo': 'juan@example.com',
                    'ci': 'V12345678',
                    'direccion': 'Av. Principal, Caracas',
                    'telefono': '+584123456789'
                }
            ],
            'facturas': [
                {
                    'id': 1,
                    'fecha': datetime.now() - timedelta(days=5),
                    'cliente_id': 1,
                    'metodo_pago': 'banco',
                    'subtotal': Decimal('1225.00'),
                    'total': Decimal('1300.00'),
                    'detalles': [
                        {
                            'producto_id': 101,
                            'cantidad': 1,
                            'precio_unitario': Decimal('1200.00'),
                            'seriales': ['SN-LAPTOP-001']
                        },
                        {
                            'producto_id': 102,
                            'cantidad': 1,
                            'precio_unitario': Decimal('25.00'),
                            'seriales': ['SN-MOUSE-001']
                        }
                    ]
                }
            ],
            'productos': [
                {
                    'id': 101,
                    'nombre': 'Laptop HP',
                    'precio_dolares': Decimal('1200.00'),
                    'cantidad_en_stock': 10
                },
                {
                    'id': 102,
                    'nombre': 'Mouse Logitech',
                    'precio_dolares': Decimal('25.00'),
                    'cantidad_en_stock': 50
                }
            ]
        }

    # ------------------------------------------
    # MOCK DE _obtener_datos_ventas
    # ------------------------------------------
    def mock_obtener_datos_ventas(self, user, fecha_inicio=None, fecha_fin=None):
        """Reemplazo estático para _obtener_datos_ventas"""
        facturas_filtradas = [
            f for f in self.datos_estaticos['facturas']
            if (not fecha_inicio or f['fecha'].date() >= fecha_inicio) and
               (not fecha_fin or f['fecha'].date() <= fecha_fin)
        ]
        
        return {
            'periodo': {
                'inicio': fecha_inicio.isoformat() if fecha_inicio else None,
                'fin': fecha_fin.isoformat() if fecha_fin else None
            },
            'total_facturas': len(facturas_filtradas),
            'productos_mas_vendidos': [
                {
                    'nombre': next(
                        p['nombre'] for p in self.datos_estaticos['productos']
                        if p['id'] == d['producto_id']
                    ),
                    'cantidad_vendida': d['cantidad']
                }
                for f in facturas_filtradas
                for d in f['detalles']
            ],
            'metodos_pago_utilizados': list(set(
                f['metodo_pago'] for f in facturas_filtradas
            ))
        }

    # ------------------------------------------
    # PRUEBA PRINCIPAL (ESTÁTICA)
    # ------------------------------------------
    @patch('tu_app.views.DeepSeekService.generate_report')
    @patch('tu_app.views.CrearReporteView._obtener_datos_ventas')
    def test_reporte_estatico_completo(
        self, 
        mock_obtener_datos,
        mock_deepseek
    ):
        # Configurar mocks
        mock_obtener_datos.side_effect = self.mock_obtener_datos_ventas
        mock_deepseek.return_value = """
            [REPORTE ESTÁTICO DE PRUEBA]
            - Productos vendidos: Laptop HP (1), Mouse Logitech (1)
            - Total facturas: 1
            - Métodos de pago: banco
        """

        # Llamar a la API
        response = self.client.post(
            '/api/crear-reporte/',
            data={
                'tipo_reporte': 'ANALISIS_VENTAS',
                'fecha_inicio': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
                'fecha_fin': datetime.now().strftime('%Y-%m-%d')
            },
            format='json'
        )

        # ------------------------------------------
        # VERIFICACIONES
        # ------------------------------------------
        self.assertEqual(response.status_code, 201)
        
        # 1. Verificar datos de entrada
        datos_entrada = response.data['datos_entrada']
        self.assertEqual(datos_entrada['total_facturas'], 1)
        self.assertEqual(len(datos_entrada['productos_mas_vendidos']), 2)
        
        # 2. Verificar producto (Laptop HP)
        laptop_data = next(
            p for p in datos_entrada['productos_mas_vendidos']
            if p['nombre'] == 'Laptop HP'
        )
        self.assertEqual(laptop_data['cantidad_vendida'], 1)

        # 3. Verificar prompt
        prompt = response.data['prompt_utilizado']
        self.assertIn('Laptop HP', prompt)
        self.assertIn('banco', prompt)  # Método de pago

        # 4. Verificar reporte generado (mock de DeepSeek)
        self.assertIn('REPORTE ESTÁTICO DE PRUEBA', response.data['reporte_generado'])

    # ------------------------------------------
    # CASOS ADICIONALES
    # ------------------------------------------
    @patch('tu_app.views.CrearReporteView._obtener_datos_ventas')
    def test_reporte_sin_facturas(self, mock_obtener_datos):
        """Prueba cuando no hay facturas en el período"""
        mock_obtener_datos.return_value = {
            'periodo': {'inicio': None, 'fin': None},
            'total_facturas': 0,
            'productos_mas_vendidos': []
        }

        response = self.client.post(
            '/api/crear-reporte/',
            data={
                'tipo_reporte': 'analisis_ventas',
                'fecha_inicio': '2025-01-01',  # Fecha futura
                'fecha_fin': '2025-01-31'
            },
            format='json'
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['datos_entrada']['total_facturas'], 0)

    @patch('tu_app.views.DeepSeekService.generate_report')
    def test_reporte_compras(self, mock_deepseek):
        # Configurar datos estáticos específicos
        self.datos_estaticos['productos'][0]['cantidad_en_stock'] = 2  # Stock bajo
        
        mock_deepseek.return_value = "Comprar 10 Laptop HP (stock bajo: 2)"
        
        response = self.client.post(
            '/api/crear-reporte/',
            data={'tipo_reporte': 'recomendacion_compras'},
            format='json'
        )
        
        self.assertIn('stock bajo', response.data['reporte_generado'])