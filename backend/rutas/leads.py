"""
rutas/leads.py — Endpoints del pipeline de leads
=================================================
Gestiona el ciclo de vida completo de un lead:
  GET  /api/leads          → Lista paginada
  POST /api/leads/detectar → Lanza el scraper
  GET  /api/leads/{id}     → Detalle de un lead
  POST /api/leads/{id}/contactar → Envía el micro-sondeo
  POST /api/leads/{id}/respuesta → Registra la respuesta del prospecto
  POST /api/leads/{id}/calificar → Simula calificación Dapta
  POST /api/leads/procesar-lote  → Procesa leads en lote
"""

import random
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from backend.base_datos.conexion import (
    insertar_lead,
    obtener_lead_por_id,
    listar_leads,
    actualizar_estado_lead,
    sumar_costo_lead,
    registrar_evento_costo,
)
from backend.modelos.lead import (
    EstadoLead, CanalContacto, SolicitudDeteccion, LeadRespuesta
)
from backend.servicios.scraper import detectar_leads
from backend.servicios.rag_agente import (
    seleccionar_micro_sondeo,
    generar_propuesta_personalizada,
    simular_calificacion_dapta,
)
from backend.servicios.contacto import enviar_micro_sondeo, enviar_propuesta


router = APIRouter(prefix="/api/leads", tags=["Leads"])


# ---------------------------------------------------------------------------
# GET /api/leads — Listar leads con filtros y paginación
# ---------------------------------------------------------------------------

@router.get("", summary="Listar leads con filtros opcionales")
def listar(
    pagina:  int           = Query(1, ge=1, description="Número de página"),
    tamano:  int           = Query(20, ge=1, le=100, description="Leads por página"),
    canal:   Optional[str] = Query(None, description="Filtrar por canal"),
    estado:  Optional[str] = Query(None, description="Filtrar por estado del pipeline"),
    sector:  Optional[str] = Query(None, description="Filtrar por sector de negocio"),
):
    """
    Retorna la lista paginada de leads con filtros opcionales.
    Útil para el dashboard y para debugging.
    """
    leads = listar_leads(
        pagina=pagina,
        tamano=tamano,
        canal=canal,
        estado=estado,
        sector=sector,
    )
    return {
        "pagina":   pagina,
        "tamano":   tamano,
        "total":    len(leads),
        "leads":    leads,
    }


# ---------------------------------------------------------------------------
# POST /api/leads/detectar — Lanzar scraper y detectar nuevos leads
# ---------------------------------------------------------------------------

@router.post("/detectar", summary="Detectar nuevos leads desde fuentes gratuitas")
def detectar(solicitud: SolicitudDeteccion):
    """
    Lanza el scraper de señales de dolor y persiste los leads detectados.

    El scraper consulta (simulado) Google Maps, portales de empleo y
    realiza auditorías web para encontrar pymes con necesidades reales.
    """
    leads_detectados = detectar_leads(
        sector          = solicitud.sector,
        ciudad          = solicitud.ciudad,
        canal_preferido = solicitud.canal_preferido,
        cantidad_maxima = solicitud.cantidad_maxima,
    )

    ids_insertados = []
    for lead in leads_detectados:
        data = lead.dict()
        data["campana_id"] = None
        data["fecha_deteccion"] = data["fecha_deteccion"].isoformat()
        if data.get("fecha_contacto"):
            data["fecha_contacto"] = data["fecha_contacto"].isoformat()
        if data.get("fecha_respuesta"):
            data["fecha_respuesta"] = data["fecha_respuesta"].isoformat()

        insertar_lead(data)

        # Registrar costo de scraping como evento atómico
        registrar_evento_costo({
            "id":          str(uuid.uuid4()),
            "lead_id":     data["id"],
            "tipo":        "scraping",
            "monto_usd":   lead.costo_scraping,
            "descripcion": f"Scraping en {lead.fuente_deteccion}",
            "timestamp":   datetime.utcnow().isoformat(),
        })
        # Registrar costo de análisis inicial con LLM
        registrar_evento_costo({
            "id":          str(uuid.uuid4()),
            "lead_id":     data["id"],
            "tipo":        "tokens_llm",
            "monto_usd":   lead.costo_tokens,
            "descripcion": "Análisis inicial de señal de dolor (LLM)",
            "timestamp":   datetime.utcnow().isoformat(),
        })

        ids_insertados.append(data["id"])

    return {
        "mensaje":          f"{len(ids_insertados)} leads detectados y guardados",
        "leads_detectados": len(ids_insertados),
        "ids":              ids_insertados,
    }


# ---------------------------------------------------------------------------
# GET /api/leads/{id} — Detalle de un lead
# ---------------------------------------------------------------------------

@router.get("/{lead_id}", summary="Obtener detalle de un lead")
def detalle(lead_id: str):
    """Retorna todos los datos de un lead específico por su ID."""
    lead = obtener_lead_por_id(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail=f"Lead '{lead_id}' no encontrado")
    return lead


# ---------------------------------------------------------------------------
# POST /api/leads/{id}/contactar — Enviar micro-sondeo
# ---------------------------------------------------------------------------

@router.post("/{lead_id}/contactar", summary="Enviar micro-sondeo al lead")
def contactar(lead_id: str):
    """
    Selecciona el micro-sondeo más apropiado usando el motor RAG y
    lo envía al lead por el canal asignado. Registra el costo exacto.
    """
    lead = obtener_lead_por_id(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")

    if lead["estado"] != EstadoLead.DETECTADO:
        raise HTTPException(
            status_code=400,
            detail=f"El lead ya fue procesado (estado: {lead['estado']})"
        )

    # 1. Generar micro-sondeo con el motor RAG
    pregunta = seleccionar_micro_sondeo(
        nombre_negocio = lead["nombre_negocio"],
        sector         = lead["sector"],
        tipo_senal     = lead["tipo_senal"],
    )

    # 2. Determinar el destinatario según el canal
    canal = CanalContacto(lead["canal"])
    if canal == CanalContacto.EMAIL:
        destinatario = lead.get("email") or "sin-email@demo.com"
    elif canal == CanalContacto.WHATSAPP:
        destinatario = lead.get("telefono") or "+57 000 000 0000"
    else:
        destinatario = lead.get("sitio_web") or "http://demo.com"

    # 3. Enviar por el canal correspondiente
    resultado = enviar_micro_sondeo(
        lead_id        = lead_id,
        canal          = canal,
        destinatario   = destinatario,
        sitio_web      = lead.get("sitio_web"),
        mensaje        = pregunta,
        nombre_negocio = lead["nombre_negocio"],
    )

    # 4. Actualizar estado y costos del lead
    actualizar_estado_lead(lead_id, EstadoLead.CONTACTADO, {
        "pregunta_sondeo": pregunta,
        "fecha_contacto":  datetime.utcnow().isoformat(),
        "costo_envio":     lead.get("costo_envio", 0.0) + resultado.costo_envio_usd,
        "costo_tokens":    lead.get("costo_tokens", 0.0) + resultado.costo_tokens_usd,
    })

    # 5. Registrar evento de costo del envío
    registrar_evento_costo({
        "id":          str(uuid.uuid4()),
        "lead_id":     lead_id,
        "tipo":        f"envio_{canal.value}",
        "monto_usd":   resultado.costo_envio_usd,
        "descripcion": f"Envío micro-sondeo por {canal.value}",
        "timestamp":   datetime.utcnow().isoformat(),
    })

    return {
        "mensaje":         "Micro-sondeo enviado exitosamente",
        "canal":           canal.value,
        "pregunta_enviada": pregunta,
        "costo_envio_usd": resultado.costo_envio_usd,
        "costo_tokens_usd": resultado.costo_tokens_usd,
    }


# ---------------------------------------------------------------------------
# POST /api/leads/{id}/respuesta — Registrar respuesta del prospecto
# ---------------------------------------------------------------------------

@router.post("/{lead_id}/respuesta", summary="Registrar respuesta del prospecto al sondeo")
def registrar_respuesta(lead_id: str, body: LeadRespuesta):
    """
    Webhook: registra que el prospecto respondió el micro-sondeo (opción A o B).
    Genera y envía automáticamente la propuesta personalizada.
    """
    lead = obtener_lead_por_id(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")

    if lead["estado"] not in [EstadoLead.CONTACTADO, EstadoLead.RESPONDIO]:
        raise HTTPException(
            status_code=400,
            detail=f"Estado inválido para registrar respuesta: {lead['estado']}"
        )

    opcion = body.opcion.upper()
    if opcion not in ["A", "B"]:
        raise HTTPException(status_code=400, detail="La opción debe ser 'A' o 'B'")

    # 1. Generar propuesta personalizada con RAG
    propuesta = generar_propuesta_personalizada(
        nombre_negocio = lead["nombre_negocio"],
        sector         = lead["sector"],
        tipo_senal     = lead["tipo_senal"],
        opcion_elegida = opcion,
    )

    # 2. Enviar la propuesta
    canal = CanalContacto(lead["canal"])
    if canal == CanalContacto.EMAIL:
        destinatario = lead.get("email") or "sin-email@demo.com"
    elif canal == CanalContacto.WHATSAPP:
        destinatario = lead.get("telefono") or "+57 000 000 0000"
    else:
        destinatario = lead.get("sitio_web") or "http://demo.com"

    resultado = enviar_propuesta(
        lead_id        = lead_id,
        canal          = canal,
        destinatario   = destinatario,
        sitio_web      = lead.get("sitio_web"),
        propuesta      = propuesta,
        nombre_negocio = lead["nombre_negocio"],
    )

    # 3. Actualizar estado del lead
    actualizar_estado_lead(lead_id, EstadoLead.RESPONDIO, {
        "opcion_respondida":  opcion,
        "propuesta_generada": propuesta,
        "fecha_respuesta":    datetime.utcnow().isoformat(),
        "costo_envio":        lead.get("costo_envio", 0.0) + resultado.costo_envio_usd,
        "costo_tokens":       lead.get("costo_tokens", 0.0) + resultado.costo_tokens_usd,
    })

    # 4. Registrar evento de costo de la propuesta
    registrar_evento_costo({
        "id":          str(uuid.uuid4()),
        "lead_id":     lead_id,
        "tipo":        "tokens_llm",
        "monto_usd":   resultado.costo_tokens_usd,
        "descripcion": "Generación de propuesta personalizada (RAG + LLM)",
        "timestamp":   datetime.utcnow().isoformat(),
    })

    return {
        "mensaje":              "Respuesta registrada y propuesta enviada",
        "opcion_elegida":       opcion,
        "propuesta_generada":   propuesta,
        "costo_propuesta_usd":  resultado.costo_total_usd,
    }


# ---------------------------------------------------------------------------
# POST /api/leads/{id}/calificar — Calificación Dapta
# ---------------------------------------------------------------------------

@router.post("/{lead_id}/calificar", summary="Calificar el lead con el agente Dapta")
def calificar(lead_id: str):
    """
    Envía el lead al agente calificador de Dapta (simulado en demo).
    Actualiza el estado a 'calificado' o 'rechazado' según el resultado.
    """
    lead = obtener_lead_por_id(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")

    if lead["estado"] != EstadoLead.RESPONDIO:
        raise HTTPException(
            status_code=400,
            detail="Solo se pueden calificar leads que respondieron el sondeo"
        )

    # Simular llamada al webhook de Dapta
    calificado, score = simular_calificacion_dapta(
        nombre_negocio   = lead["nombre_negocio"],
        sector           = lead["sector"],
        opcion_elegida   = lead.get("opcion_respondida"),
        propuesta_enviada= bool(lead.get("propuesta_generada")),
    )

    nuevo_estado = EstadoLead.CALIFICADO if calificado else EstadoLead.RECHAZADO

    actualizar_estado_lead(lead_id, nuevo_estado, {
        "calificado_dapta":    1 if calificado else 0,
        "score_calidad_dapta": score,
    })

    return {
        "mensaje":             f"Lead {'calificado ✅' if calificado else 'rechazado ❌'} por Dapta",
        "calificado":          calificado,
        "score_calidad":       score,
        "nuevo_estado":        nuevo_estado,
    }


# ---------------------------------------------------------------------------
# POST /api/leads/procesar-lote — Procesar todos los leads de una etapa
# ---------------------------------------------------------------------------

class SolicitudLote(BaseModel):
    """Parámetros para procesar un lote de leads."""
    accion: str  # "contactar", "respuesta", "calificar"
    limite: int = 50  # Máximo de leads a procesar

@router.post("/procesar-lote", summary="Procesar un lote de leads en una acción")
def procesar_lote(solicitud: SolicitudLote):
    """
    Procesa múltiples leads de una etapa del pipeline en lote.
    Útil para avanzar rápidamente en la demostración.
    
    Acciones:
      - "contactar":  Contacta todos los leads en estado 'detectado'
      - "respuesta":  Simula respuesta de todos los leads en estado 'contactado'
      - "calificar":  Califica todos los leads en estado 'respondio'
    """
    # Map action to required state
    mapa_estado_requerido = {
        "contactar": EstadoLead.DETECTADO,
        "respuesta": EstadoLead.CONTACTADO,
        "calificar": EstadoLead.RESPONDIO,
    }
    
    estado_requerido = mapa_estado_requerido.get(solicitud.accion)
    if not estado_requerido:
        raise HTTPException(status_code=400, detail=f"Acción '{solicitud.accion}' no válida. Use: contactar, respuesta, calificar")
    
    # Get leads in the required state
    todos_leads = listar_leads(pagina=1, tamano=solicitud.limite, estado=estado_requerido)
    
    resultados = []
    errores = 0
    
    for lead_data in todos_leads:
        try:
            lead_id = lead_data["id"]
            if solicitud.accion == "contactar":
                contactar(lead_id)
            elif solicitud.accion == "respuesta":
                import random
                opcion = random.choice(["A", "B"])
                registrar_respuesta(lead_id, LeadRespuesta(lead_id=lead_id, opcion=opcion))
            elif solicitud.accion == "calificar":
                calificar(lead_id)
            resultados.append(lead_id)
        except Exception as e:
            errores += 1
            print(f"[LOTE] Error procesando lead {lead_data.get('id', '?')}: {e}")
    
    return {
        "mensaje": f"{len(resultados)} leads procesados con acción '{solicitud.accion}'",
        "procesados": len(resultados),
        "errores": errores,
        "ids_procesados": resultados,
    }
