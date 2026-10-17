"""
modelos/lead.py — Modelos de datos del dominio principal
=========================================================
Define las estructuras de datos (dataclasses + Pydantic) para:
  - Lead: un prospecto detectado con su señal de dolor y estado actual
  - EventoCosto: cada centavo gastado en un lead (scraping, tokens, envío)
  - EstadoLead: enum del ciclo de vida completo de un prospecto
  - CanalContacto: canales disponibles de salida
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enumeraciones
# ---------------------------------------------------------------------------

class EstadoLead(str, Enum):
    """
    Ciclo de vida de un lead a través del pipeline.
    El orden es: detectado → contactado → respondio → calificado / rechazado
    """
    DETECTADO    = "detectado"      # Extraído del scraper, aún sin contacto
    CONTACTADO   = "contactado"     # Se le envió el micro-sondeo
    RESPONDIO    = "respondio"      # Respondió la pregunta de sondeo (opción A o B)
    CALIFICADO   = "calificado"     # Aprobado por el agente Dapta
    RECHAZADO    = "rechazado"      # Dapta lo descartó o no respondió


class CanalContacto(str, Enum):
    """Canales de salida disponibles para contactar leads."""
    EMAIL          = "email"
    WHATSAPP       = "whatsapp"
    FORMULARIO_WEB = "formulario_web"


class FuenteDeteccion(str, Enum):
    """Fuentes gratuitas de donde proviene el lead."""
    GOOGLE_MAPS       = "google_maps"
    PORTAL_EMPLEO     = "portal_empleo"
    AUDITORIA_WEB     = "auditoria_web"


# ---------------------------------------------------------------------------
# Modelo principal: Lead
# ---------------------------------------------------------------------------

class Lead(BaseModel):
    """
    Representa a un prospecto (pyme) detectado con señal de dolor real.
    Cada campo registra la información que permite calcular el CPL exacto.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    # -- Datos del negocio --
    nombre_negocio:  str
    sector:          str                     # Ej: "restaurante", "clinica", "taller"
    ciudad:          Optional[str] = None
    telefono:        Optional[str] = None
    email:           Optional[str] = None
    sitio_web:       Optional[str] = None

    # -- Señal de dolor detectada --
    senal_dolor:      str   # Texto público que justifica el contacto
    tipo_senal:       str   # Ej: "reseña_negativa", "vacante_ventas", "sin_whatsapp"
    fuente_deteccion: FuenteDeteccion = FuenteDeteccion.GOOGLE_MAPS

    # -- Canal asignado para el outreach --
    canal: CanalContacto = CanalContacto.EMAIL

    # -- Estado en el pipeline --
    estado: EstadoLead = EstadoLead.DETECTADO

    # -- Micro-sondeo y respuesta --
    pregunta_sondeo:     Optional[str] = None   # Pregunta de 1 clic enviada
    opcion_respondida:   Optional[str] = None   # "A" o "B"
    propuesta_generada:  Optional[str] = None   # Propuesta personalizada enviada

    # -- Calificación Dapta --
    calificado_dapta:    bool  = False
    score_calidad_dapta: float = 0.0

    # -- Costos acumulados (se actualizan en cada evento) --
    costo_scraping: float = 0.0
    costo_tokens:   float = 0.0
    costo_envio:    float = 0.0

    @property
    def costo_total(self) -> float:
        """Suma de todos los costos asociados a este lead."""
        return self.costo_scraping + self.costo_tokens + self.costo_envio

    # -- Timestamps --
    fecha_deteccion: datetime = Field(default_factory=datetime.utcnow)
    fecha_contacto:  Optional[datetime] = None
    fecha_respuesta: Optional[datetime] = None

    class Config:
        use_enum_values = True


# ---------------------------------------------------------------------------
# Modelo: EventoCosto
# ---------------------------------------------------------------------------

class EventoCosto(BaseModel):
    """
    Registro atómico de cada gasto operativo asociado a un lead.
    Permite auditar exactamente dónde se gasta cada centavo.
    """
    id:           str = Field(default_factory=lambda: str(uuid.uuid4()))
    lead_id:      str
    tipo:         str    # "scraping", "tokens_llm", "envio_email", "envio_whatsapp"
    monto_usd:    float  # Monto exacto en dólares
    descripcion:  str    # Descripción legible del gasto
    timestamp:    datetime = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# Schemas Pydantic para la API (request/response)
# ---------------------------------------------------------------------------

class LeadCrear(BaseModel):
    """Schema para crear un lead manualmente (para testing)."""
    nombre_negocio:   str
    sector:           str
    ciudad:           Optional[str] = None
    telefono:         Optional[str] = None
    email:            Optional[str] = None
    sitio_web:        Optional[str] = None
    senal_dolor:      str
    tipo_senal:       str
    canal:            CanalContacto = CanalContacto.EMAIL


class LeadRespuesta(BaseModel):
    """Schema de respuesta al registrar la opción elegida por el prospecto."""
    lead_id:         str
    opcion:          str   # "A" o "B"


class SolicitudDeteccion(BaseModel):
    """Parámetros para lanzar el scraper y detectar nuevos leads."""
    sector:           Optional[str] = None    # Filtrar por sector
    ciudad:           Optional[str] = None
    canal_preferido:  CanalContacto = CanalContacto.EMAIL
    cantidad_maxima:  int = 20
