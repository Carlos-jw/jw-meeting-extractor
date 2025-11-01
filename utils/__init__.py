"""
Utils module - Herramientas para extracción y generación
"""

__version__ = '1.0.0'
__author__ = 'JW Meeting Extractor'

from .jw_scraper import extraer_indice_semanas, extraer_datos_semana
from .template_generator import generar_plantilla_editable

__all__ = [
    'extraer_indice_semanas',
    'extraer_datos_semana',
    'generar_plantilla_editable'
]
