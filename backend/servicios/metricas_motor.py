"""
servicios/metricas_motor.py — Motor de cálculo de CPL y unit economics
=======================================================================
Calcula en tiempo real el Costo por Lead (CPL) Bruto y Calificado
para cada canal, consultando directamente la base de datos SQLite.

Fórmulas:
  CPL Bruto      = Σ costos del canal / total leads que respondieron el sondeo
  CPL Calificado = Σ costos del canal / total leads aprobados por Dapta

El valor diferenciador es que muestra que un canal más caro en envío
(WhatsApp) puede tener un CPL calificado más bajo por su tasa de conversión.
"""

from backend.base_datos.conexion import contar_leads_por_estado_y_canal
from backend.modelos.metricas import MetricaCanal, ResumenCPL, DatoFunnel
from backend.modelos.lead import EstadoLead, CanalContacto


# ---------------------------------------------------------------------------
# Nombres legibles de los canales para el dashboard
# ---------------------------------------------------------------------------

_NOMBRES_CANALES = {
    "email":          "Email Transaccional",
    "whatsapp":       "WhatsApp Cloud API",
    "formulario_web": "Formulario Web",
}

_TODOS_LOS_CANALES = list(CanalContacto)


# ---------------------------------------------------------------------------
# Función principal: calcular métricas por canal
# ---------------------------------------------------------------------------

def calcular_metricas_por_canal() -> list[MetricaCanal]:
    """
    Consulta la base de datos y calcula el CPL Bruto y Calificado
    para cada canal en tiempo real.

    Retorna una lista de MetricaCanal con todas las métricas calculadas.
    """
    # Obtener agrupaciones desde la DB
    filas = contar_leads_por_estado_y_canal()

    # Inicializar métricas vacías para cada canal conocido
    metricas_por_canal: dict[str, MetricaCanal] = {}
    for canal in _TODOS_LOS_CANALES:
        clave = canal.value
        metricas_por_canal[clave] = MetricaCanal(
            nombre   = _NOMBRES_CANALES.get(clave, clave.replace("_", " ").title()),
            canal_id = clave,
        )

    # Acumular datos de la DB
    for fila in filas:
        canal_id = fila["canal"]
        estado   = fila["estado"]
        cantidad = fila["cantidad"]

        # Si el canal no está en el mapa (por datos legacy), agregarlo
        if canal_id not in metricas_por_canal:
            metricas_por_canal[canal_id] = MetricaCanal(
                nombre   = canal_id.replace("_", " ").title(),
                canal_id = canal_id,
            )

        m = metricas_por_canal[canal_id]

        # Acumular costos (presentes en todas las filas del canal)
        m.costo_scraping_total += fila.get("total_scraping", 0.0) or 0.0
        m.costo_tokens_total   += fila.get("total_tokens", 0.0) or 0.0
        m.costo_envio_total    += fila.get("total_envio", 0.0) or 0.0

        # Acumular contadores acumulativos del funnel:
        # Cada etapa incluye a los leads que avanzaron a las etapas posteriores.
        m.total_detectados += cantidad  # Todos los leads fueron detectados

        etapas_posteriores_contacto = [
            EstadoLead.CONTACTADO,
            EstadoLead.RESPONDIO,
            EstadoLead.CALIFICADO,
            EstadoLead.NO_CALIFICADO,
            EstadoLead.EN_REVISION,
            EstadoLead.RECHAZADO,
        ]
        if estado in etapas_posteriores_contacto or estado in [e.value for e in etapas_posteriores_contacto]:
            m.total_contactados += cantidad

        etapas_posteriores_respuesta = [
            EstadoLead.RESPONDIO,
            EstadoLead.CALIFICADO,
            EstadoLead.NO_CALIFICADO,
            EstadoLead.EN_REVISION,
            EstadoLead.RECHAZADO,
        ]
        if estado in etapas_posteriores_respuesta or estado in [e.value for e in etapas_posteriores_respuesta]:
            m.total_respondieron += cantidad

        if estado == EstadoLead.CALIFICADO or estado == EstadoLead.CALIFICADO.value:
            m.total_calificados += cantidad

    # Para los canales que tienen datos, recalcular totales sin duplicar costos
    # (la DB devuelve costos por estado, necesitamos el total del canal)
    metricas_final = _recalcular_costos_sin_duplicar(metricas_por_canal, filas)

    return list(metricas_final.values())


def _recalcular_costos_sin_duplicar(
    metricas: dict[str, MetricaCanal],
    filas: list[dict],
) -> dict[str, MetricaCanal]:
    """
    Recalcula los costos acumulados sin duplicar por estado.
    La DB devuelve una fila por (canal, estado), pero los costos
    se acumulan en el lead independientemente del estado.
    Solución: sumar costos solo de TODOS los estados por canal.
    """
    # Reiniciar costos y recalcularlos como suma única por canal
    costos_por_canal: dict[str, dict] = {}

    for fila in filas:
        canal_id = fila["canal"]
        if canal_id not in costos_por_canal:
            costos_por_canal[canal_id] = {
                "scraping": 0.0, "tokens": 0.0, "envio": 0.0
            }
        costos_por_canal[canal_id]["scraping"] += fila.get("total_scraping", 0.0) or 0.0
        costos_por_canal[canal_id]["tokens"]   += fila.get("total_tokens", 0.0) or 0.0
        costos_por_canal[canal_id]["envio"]    += fila.get("total_envio", 0.0) or 0.0

    for canal_id, costos in costos_por_canal.items():
        if canal_id in metricas:
            metricas[canal_id].costo_scraping_total = round(costos["scraping"], 6)
            metricas[canal_id].costo_tokens_total   = round(costos["tokens"], 6)
            metricas[canal_id].costo_envio_total    = round(costos["envio"], 6)

    return metricas


def calcular_resumen_global() -> ResumenCPL:
    """
    Calcula el resumen global del sistema con todas las métricas.
    Incluye el canal ganador (menor CPL calificado) y el CPL promedio.
    """
    canales = calcular_metricas_por_canal()
    total_leads = sum(c.total_detectados for c in canales)
    total_calificados = sum(c.total_calificados for c in canales)
    costo_total = sum(c.costo_operativo_total for c in canales)

    return ResumenCPL(
        canales             = canales,
        total_leads_sistema = total_leads,
        total_calificados   = total_calificados,
        costo_total_usd     = round(costo_total, 4),
    )


def calcular_datos_funnel() -> list[DatoFunnel]:
    """
    Calcula los datos del funnel de conversión para el gráfico visual.
    Retorna etapas con cantidades absolutas y porcentajes de conversión.
    """
    metricas = calcular_metricas_por_canal()

    total_detectados  = sum(m.total_detectados for m in metricas)
    total_contactados = sum(m.total_contactados for m in metricas)
    total_respondieron = sum(m.total_respondieron for m in metricas)
    total_calificados = sum(m.total_calificados for m in metricas)

    def pct(num, den):
        return round(num / den * 100, 1) if den > 0 else 0.0

    return [
        DatoFunnel(
            etapa    = "Detectados",
            cantidad = total_detectados,
            porcentaje = 100.0,
            color    = "#6366f1",  # Indigo
        ),
        DatoFunnel(
            etapa    = "Contactados",
            cantidad = total_contactados,
            porcentaje = pct(total_contactados, total_detectados),
            color    = "#f59e0b",  # Amber
        ),
        DatoFunnel(
            etapa    = "Respondieron",
            cantidad = total_respondieron,
            porcentaje = pct(total_respondieron, total_contactados),
            color    = "#3b82f6",  # Blue
        ),
        DatoFunnel(
            etapa    = "Calificados",
            cantidad = total_calificados,
            porcentaje = pct(total_calificados, total_respondieron),
            color    = "#10b981",  # Emerald
        ),
    ]


def obtener_metricas_demo() -> list[dict]:
    """
    Retorna datos de demostración cuando la DB está vacía.
    Útil para mostrar el dashboard en la presentación sin datos reales.
    """
    return [
        {
            "nombre":              "Email Transaccional",
            "canal_id":            "email",
            "total_detectados":    45,
            "total_contactados":   45,
            "total_respondieron":  8,
            "total_calificados":   3,
            "costo_operativo_total": 0.0328,
            "tasa_respuesta":      17.8,
            "tasa_calificacion":   37.5,
            "cpl_bruto":           0.12,
            "cpl_calificado":      1.10,
            "prospectos":          45,
        },
        {
            "nombre":              "WhatsApp Cloud API",
            "canal_id":            "whatsapp",
            "total_detectados":    120,
            "total_contactados":   120,
            "total_respondieron":  34,
            "total_calificados":   14,
            "costo_operativo_total": 4.248,
            "tasa_respuesta":      28.3,
            "tasa_calificacion":   41.2,
            "cpl_bruto":           0.25,
            "cpl_calificado":      0.85,
            "prospectos":          120,
        },
        {
            "nombre":              "Formulario Web",
            "canal_id":            "formulario_web",
            "total_detectados":    30,
            "total_contactados":   30,
            "total_respondieron":  7,
            "total_calificados":   5,
            "costo_operativo_total": 0.009,
            "tasa_respuesta":      23.3,
            "tasa_calificacion":   71.4,
            "cpl_bruto":           0.05,
            "cpl_calificado":      0.65,
            "prospectos":          30,
        },
    ]
