"""
base_datos/__init__.py
"""
from .conexion import (
    inicializar_base_datos,
    insertar_lead,
    obtener_lead_por_id,
    listar_leads,
    actualizar_estado_lead,
    sumar_costo_lead,
    contar_leads_por_estado_y_canal,
    registrar_evento_costo,
    insertar_campana,
    listar_campanas,
)

__all__ = [
    "inicializar_base_datos",
    "insertar_lead",
    "obtener_lead_por_id",
    "listar_leads",
    "actualizar_estado_lead",
    "sumar_costo_lead",
    "contar_leads_por_estado_y_canal",
    "registrar_evento_costo",
    "insertar_campana",
    "listar_campanas",
]
