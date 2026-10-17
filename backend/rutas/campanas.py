"""
rutas/campanas.py — Endpoints de gestión de campañas
=====================================================
Una campaña agrupa leads por sector y canal para facilitar
el seguimiento de múltiples iniciativas en paralelo.

  GET  /api/campanas          → Listar campañas
  POST /api/campanas          → Crear nueva campaña
  GET  /api/campanas/{id}     → Estadísticas de una campaña
"""

import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from backend.base_datos.conexion import insertar_campana, listar_campanas, listar_leads


router = APIRouter(prefix="/api/campanas", tags=["Campañas"])


# ---------------------------------------------------------------------------
# Schema de solicitud de creación de campaña
# ---------------------------------------------------------------------------

class SolicitudCampana(BaseModel):
    """Datos requeridos para crear una nueva campaña."""
    nombre:          str
    sector_objetivo: Optional[str] = None
    canal:           str = "email"    # email | whatsapp | formulario_web


# ---------------------------------------------------------------------------
# GET /api/campanas
# ---------------------------------------------------------------------------

@router.get("", summary="Listar todas las campañas activas")
def listar():
    """Retorna todas las campañas con sus metadatos básicos."""
    campanas = listar_campanas()
    return {"campanas": campanas, "total": len(campanas)}


# ---------------------------------------------------------------------------
# POST /api/campanas — Crear nueva campaña
# ---------------------------------------------------------------------------

@router.post("", summary="Crear una nueva campaña")
def crear(solicitud: SolicitudCampana):
    """
    Crea una nueva campaña de prospección.
    Una campaña define el sector objetivo y el canal de contacto.
    """
    nueva_campana = {
        "id":              str(uuid.uuid4()),
        "nombre":          solicitud.nombre,
        "sector_objetivo": solicitud.sector_objetivo,
        "canal":           solicitud.canal,
        "estado":          "activa",
        "fecha_inicio":    datetime.utcnow().isoformat(),
    }
    id_campana = insertar_campana(nueva_campana)

    return {
        "mensaje":   "Campaña creada exitosamente",
        "campana_id": id_campana,
        "campana":   nueva_campana,
    }


# ---------------------------------------------------------------------------
# GET /api/campanas/{id} — Estadísticas de una campaña
# ---------------------------------------------------------------------------

@router.get("/{campana_id}/estadisticas", summary="Estadísticas de una campaña específica")
def estadisticas(campana_id: str):
    """
    Retorna las estadísticas de la campaña:
    leads detectados, contactados, respondieron y calificados.
    """
    # Buscar leads de esta campaña
    todos_los_leads = listar_leads(pagina=1, tamano=1000)
    leads_campana = [l for l in todos_los_leads if l.get("campana_id") == campana_id]

    # Calcular estadísticas de estado
    stats_estado = {}
    for lead in leads_campana:
        estado = lead.get("estado", "desconocido")
        stats_estado[estado] = stats_estado.get(estado, 0) + 1

    # Calcular costos acumulados de la campaña
    costo_total = sum(
        (l.get("costo_scraping", 0) or 0) +
        (l.get("costo_tokens", 0) or 0) +
        (l.get("costo_envio", 0) or 0)
        for l in leads_campana
    )

    calificados = stats_estado.get("calificado", 0)
    cpl_calificado = round(costo_total / calificados, 4) if calificados > 0 else 0.0

    return {
        "campana_id":    campana_id,
        "total_leads":   len(leads_campana),
        "por_estado":    stats_estado,
        "costo_total_usd": round(costo_total, 4),
        "cpl_calificado":  cpl_calificado,
    }
