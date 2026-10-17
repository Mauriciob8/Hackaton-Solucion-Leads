"""
rutas/metricas.py — Endpoints de métricas y unit economics
===========================================================
Expone el calculador en vivo de CPL que es el argumento ganador
del hackathon: muestra exactamente qué canal genera el lead más barato.

  GET /api/metricas          → Métricas por canal (compatible con frontend existente)
  GET /api/metricas/cpl      → CPL Bruto y Calificado detallado
  GET /api/metricas/funnel   → Datos del funnel de conversión
  GET /api/metricas/resumen  → Resumen global con canal ganador
"""

from fastapi import APIRouter, Query
from typing import Optional

from backend.servicios.metricas_motor import (
    calcular_metricas_por_canal,
    calcular_resumen_global,
    calcular_datos_funnel,
    obtener_metricas_demo,
)


router = APIRouter(prefix="/api/metricas", tags=["Métricas"])


# ---------------------------------------------------------------------------
# GET /api/metricas — Endpoint principal (compatible con frontend existente)
# ---------------------------------------------------------------------------

@router.get("", summary="Métricas de CPL por canal en tiempo real")
def get_metricas(
    modo_demo: Optional[bool] = Query(
        False,
        description="Si True, retorna datos de demostración aunque la DB esté vacía"
    )
):
    """
    Endpoint principal de métricas. Retorna CPL Bruto y Calificado
    por canal, calculados en tiempo real desde la base de datos.

    Compatible con el formato que espera el frontend existente.
    Si no hay datos reales, retorna datos de demostración.
    """
    metricas = calcular_metricas_por_canal()

    # Si no hay datos reales (DB vacía) o se pide modo demo, usar datos de demo
    tiene_datos = any(m.total_detectados > 0 for m in metricas)
    if not tiene_datos or modo_demo:
        datos_demo = obtener_metricas_demo()
        return {
            "canales":    datos_demo,
            "modo_demo":  True,
            "mensaje":    "Mostrando datos de demostración. Detecte leads para ver datos reales.",
        }

    return {
        "canales":    [m.to_dict_api() for m in metricas],
        "modo_demo":  False,
    }


# ---------------------------------------------------------------------------
# GET /api/metricas/cpl — CPL detallado por canal
# ---------------------------------------------------------------------------

@router.get("/cpl", summary="CPL Bruto y Calificado detallado por canal")
def get_cpl():
    """
    Retorna el desglose completo de CPL por canal con todas las métricas
    de conversión: tasa de respuesta, tasa de calificación, costos.

    Fórmulas:
      CPL Bruto      = costos totales / leads que respondieron el sondeo
      CPL Calificado = costos totales / leads aprobados por Dapta
    """
    resumen = calcular_resumen_global()
    canal_ganador = resumen.canal_ganador

    resultado = {
        "canales": [m.to_dict_api() for m in resumen.canales],
        "resumen_global": {
            "total_leads":       resumen.total_leads_sistema,
            "total_calificados": resumen.total_calificados,
            "costo_total_usd":   resumen.costo_total_usd,
            "cpl_promedio":      resumen.cpl_promedio_global,
        },
        "canal_ganador": {
            "nombre":        canal_ganador.nombre if canal_ganador else None,
            "canal_id":      canal_ganador.canal_id if canal_ganador else None,
            "cpl_calificado": canal_ganador.cpl_calificado if canal_ganador else None,
        },
    }

    return resultado


# ---------------------------------------------------------------------------
# GET /api/metricas/funnel — Datos del funnel de conversión
# ---------------------------------------------------------------------------

@router.get("/funnel", summary="Datos del funnel de conversión por etapa")
def get_funnel():
    """
    Retorna el conteo de leads en cada etapa del funnel:
    Detectados → Contactados → Respondieron → Calificados

    Con porcentajes de conversión entre etapas.
    """
    datos_funnel = calcular_datos_funnel()

    # Si no hay datos, retornar datos demo del funnel
    if not datos_funnel or all(d.cantidad == 0 for d in datos_funnel):
        return {
            "etapas": [
                {"etapa": "Detectados",  "cantidad": 195, "porcentaje": 100.0, "color": "#6366f1"},
                {"etapa": "Contactados", "cantidad": 195, "porcentaje": 100.0, "color": "#f59e0b"},
                {"etapa": "Respondieron","cantidad": 49,  "porcentaje": 25.1,  "color": "#3b82f6"},
                {"etapa": "Calificados", "cantidad": 22,  "porcentaje": 44.9,  "color": "#10b981"},
            ],
            "modo_demo": True,
        }

    return {
        "etapas":    [d.dict() for d in datos_funnel],
        "modo_demo": False,
    }


# ---------------------------------------------------------------------------
# GET /api/metricas/resumen — Resumen ejecutivo global
# ---------------------------------------------------------------------------

@router.get("/resumen", summary="Resumen ejecutivo global del sistema")
def get_resumen():
    """
    Retorna el resumen ejecutivo con KPIs globales:
    total de leads, calificados, costo total y canal con menor CPL.
    """
    resumen = calcular_resumen_global()
    canal_ganador = resumen.canal_ganador

    return {
        "total_leads_sistema": resumen.total_leads_sistema,
        "total_calificados":   resumen.total_calificados,
        "costo_total_usd":     resumen.costo_total_usd,
        "cpl_promedio_global": resumen.cpl_promedio_global,
        "canal_mas_eficiente": canal_ganador.nombre if canal_ganador else "Sin datos",
        "mejor_cpl_calificado": canal_ganador.cpl_calificado if canal_ganador else 0.0,
    }
