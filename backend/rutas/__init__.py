"""
rutas/__init__.py
"""
from .leads import router as router_leads
from .campanas import router as router_campanas
from .metricas import router as router_metricas

__all__ = ["router_leads", "router_campanas", "router_metricas"]
