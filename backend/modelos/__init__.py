"""
modelos/__init__.py — Exportaciones del paquete de modelos
"""
from .lead import Lead, EventoCosto, EstadoLead, CanalContacto, FuenteDeteccion
from .metricas import MetricaCanal, ResumenCPL, DatoFunnel

__all__ = [
    "Lead", "EventoCosto", "EstadoLead", "CanalContacto", "FuenteDeteccion",
    "MetricaCanal", "ResumenCPL", "DatoFunnel",
]
