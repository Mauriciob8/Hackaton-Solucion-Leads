"""
servicios/__init__.py
"""
from .scraper import detectar_leads
from .rag_agente import (
    seleccionar_micro_sondeo,
    generar_propuesta_personalizada,
    calificar_con_agente_dapta,
)
from .contacto import enviar_micro_sondeo, enviar_propuesta
from .metricas_motor import calcular_metricas_por_canal, calcular_resumen_global, calcular_datos_funnel, obtener_metricas_demo

__all__ = [
    "detectar_leads",
    "seleccionar_micro_sondeo",
    "generar_propuesta_personalizada",
    "calificar_con_agente_dapta",
    "enviar_micro_sondeo",
    "enviar_propuesta",
    "calcular_metricas_por_canal",
    "calcular_resumen_global",
    "calcular_datos_funnel",
    "obtener_metricas_demo",
]
