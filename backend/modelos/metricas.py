"""
modelos/metricas.py — Modelos de métricas y unit economics
===========================================================
Encapsula las fórmulas de CPL (Costo por Lead) y los datos necesarios
para comparar canales en el dashboard.

Fórmulas clave:
  CPL Bruto      = Σ(costos del canal) / total_leads_que_respondieron
  CPL Calificado = Σ(costos del canal) / total_leads_aprobados_dapta
"""

from pydantic import BaseModel
from typing import Optional


class MetricaCanal(BaseModel):
    """
    Resumen de desempeño y costo de un canal de contacto específico.
    Se computa en tiempo real a partir de los EventoCosto registrados.
    """
    nombre:               str    # Nombre legible del canal (ej: "WhatsApp API")
    canal_id:             str    # Clave del canal (ej: "whatsapp")

    # Contadores del funnel
    total_detectados:     int = 0   # Leads detectados asignados a este canal
    total_contactados:    int = 0   # Leads a los que se envió el sondeo
    total_respondieron:   int = 0   # Leads que respondieron la pregunta
    total_calificados:    int = 0   # Leads aprobados por Dapta

    # Costos acumulados en USD
    costo_scraping_total: float = 0.0
    costo_tokens_total:   float = 0.0
    costo_envio_total:    float = 0.0

    @property
    def costo_operativo_total(self) -> float:
        """Suma de todos los costos del canal."""
        return (
            self.costo_scraping_total +
            self.costo_tokens_total +
            self.costo_envio_total
        )

    @property
    def tasa_respuesta(self) -> float:
        """Porcentaje de leads contactados que respondieron el sondeo."""
        if self.total_contactados == 0:
            return 0.0
        return round(self.total_respondieron / self.total_contactados * 100, 1)

    @property
    def tasa_calificacion(self) -> float:
        """Porcentaje de leads que respondieron y fueron calificados por Dapta."""
        if self.total_respondieron == 0:
            return 0.0
        return round(self.total_calificados / self.total_respondieron * 100, 1)

    @property
    def cpl_bruto(self) -> float:
        """
        CPL Bruto = costos totales / leads que respondieron el sondeo.
        Mide el costo de conseguir cualquier interacción.
        """
        if self.total_respondieron == 0:
            return 0.0
        return round(self.costo_operativo_total / self.total_respondieron, 4)

    @property
    def cpl_calificado(self) -> float:
        """
        CPL Calificado = costos totales / leads aprobados por Dapta.
        Es la métrica principal: cuánto cuesta un lead que REALMENTE sirve.
        """
        if self.total_calificados == 0:
            return 0.0
        return round(self.costo_operativo_total / self.total_calificados, 4)

    def to_dict_api(self) -> dict:
        """Serialización completa para la respuesta de la API."""
        return {
            "nombre": self.nombre,
            "canal_id": self.canal_id,
            "total_detectados": self.total_detectados,
            "total_contactados": self.total_contactados,
            "total_respondieron": self.total_respondieron,
            "total_calificados": self.total_calificados,
            "costo_operativo_total": round(self.costo_operativo_total, 4),
            "tasa_respuesta": self.tasa_respuesta,
            "tasa_calificacion": self.tasa_calificacion,
            "cpl_bruto": self.cpl_bruto,
            "cpl_calificado": self.cpl_calificado,
            # Alias para compatibilidad con el frontend existente
            "cpl_bruto_alias": self.cpl_bruto,
            "prospectos": self.total_detectados,
        }


class ResumenCPL(BaseModel):
    """
    Resumen global del sistema con todas las métricas agregadas.
    Incluye el ranking de canales y el canal ganador (menor CPL calificado).
    """
    canales:             list[MetricaCanal]
    total_leads_sistema: int = 0
    total_calificados:   int = 0
    costo_total_usd:     float = 0.0

    @property
    def canal_ganador(self) -> Optional[MetricaCanal]:
        """Retorna el canal con el menor CPL calificado (>0)."""
        canales_activos = [c for c in self.canales if c.cpl_calificado > 0]
        if not canales_activos:
            return None
        return min(canales_activos, key=lambda c: c.cpl_calificado)

    @property
    def cpl_promedio_global(self) -> float:
        """CPL calificado promedio ponderado de todos los canales."""
        if self.total_calificados == 0:
            return 0.0
        return round(self.costo_total_usd / self.total_calificados, 4)


class DatoFunnel(BaseModel):
    """Datos de un paso del funnel para el gráfico de conversión."""
    etapa:       str    # "Detectados", "Contactados", "Respondieron", "Calificados"
    cantidad:    int
    porcentaje:  float  # Relativo a la etapa anterior
    color:       str    # Clase CSS o color hex para el frontend
