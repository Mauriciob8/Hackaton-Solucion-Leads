"""
servicios/contacto.py — Servicio de contacto multi-canal
=========================================================
Gestiona el envío del micro-sondeo y la propuesta personalizada
a través de los canales disponibles (Email, WhatsApp, Formulario Web).

Cada envío registra el costo exacto en la tabla eventos_costo para
que el calculador de CPL tenga datos precisos.

NOTA DEMO: Los envíos se simulan (se loguean). Para producción:
  - Email:     descomentar integración con Resend API
  - WhatsApp:  descomentar integración con WhatsApp Cloud API
  - Formulario: usar Playwright para automatizar formularios web reales
"""

import sys
import uuid
from datetime import datetime
from typing import Optional

from backend.config import COSTOS_CANAL, COSTO_TOKENS_LLM_POR_LEAD
from backend.modelos.lead import CanalContacto


def _log_seguro(texto: str):
    """Imprime mensajes de log protegiendo contra errores de codificación en consolas Windows."""
    try:
        print(texto)
    except UnicodeEncodeError:
        print(texto.encode("ascii", errors="replace").decode("ascii"))


# ---------------------------------------------------------------------------
# Resultado de envío
# ---------------------------------------------------------------------------

class ResultadoEnvio:
    """Encapsula el resultado de un envío con todos los costos incurridos."""

    def __init__(
        self,
        exito:           bool,
        canal:           str,
        costo_envio_usd: float,
        costo_tokens_usd: float,
        mensaje_enviado: str,
        detalle:         str = "",
    ):
        self.exito            = exito
        self.canal            = canal
        self.costo_envio_usd  = costo_envio_usd
        self.costo_tokens_usd = costo_tokens_usd
        self.mensaje_enviado  = mensaje_enviado
        self.detalle          = detalle
        self.timestamp        = datetime.utcnow()

    @property
    def costo_total_usd(self) -> float:
        return self.costo_envio_usd + self.costo_tokens_usd


# ---------------------------------------------------------------------------
# Simuladores de envío por canal
# ---------------------------------------------------------------------------

def _enviar_email_simulado(
    destinatario: str,
    asunto: str,
    cuerpo: str,
) -> dict:
    """
    Simula el envío de un email transaccional.
    En producción: conectar con Resend API (resend.com)

    Costo real: ~$0.0002 USD por email (Amazon SES / Resend)
    """
    _log_seguro(f"[EMAIL SIMULADO] Para: {destinatario}")
    _log_seguro(f"[EMAIL SIMULADO] Asunto: {asunto}")
    _log_seguro(f"[EMAIL SIMULADO] ---\n{cuerpo[:200]}...\n---")

    # En producción sería algo como:
    # import resend
    # resend.api_key = RESEND_API_KEY
    # response = resend.Emails.send({...})

    return {"status": "simulado", "mensaje_id": str(uuid.uuid4())}


def _enviar_whatsapp_simulado(
    numero: str,
    mensaje: str,
) -> dict:
    """
    Simula el envío por WhatsApp Cloud API.
    En producción: conectar con Meta WhatsApp Business API

    Costo real: ~$0.0350 USD por conversación iniciada por empresa (Tier 1 LatAm)
    """
    _log_seguro(f"[WHATSAPP SIMULADO] Para: {numero}")
    _log_seguro(f"[WHATSAPP SIMULADO] Mensaje: {mensaje[:200]}...")

    # En producción sería algo como:
    # import httpx
    # httpx.post(f"https://graph.facebook.com/v18.0/{PHONE_ID}/messages",
    #            headers={"Authorization": f"Bearer {WA_TOKEN}"},
    #            json={"messaging_product": "whatsapp", "to": numero, "type": "text",
    #                  "text": {"body": mensaje}})

    return {"status": "simulado", "wa_message_id": str(uuid.uuid4())}


def _enviar_formulario_web_simulado(
    url_sitio: str,
    mensaje: str,
) -> dict:
    """
    Simula el envío por formulario de contacto web usando Playwright.
    En producción: automatizar el llenado del formulario del sitio.

    Costo real: $0.0000 USD de envío (solo costo de tokens de análisis)
    """
    _log_seguro(f"[FORMULARIO WEB SIMULADO] Sitio: {url_sitio}")
    _log_seguro(f"[FORMULARIO WEB SIMULADO] Mensaje: {mensaje[:200]}...")

    # En producción sería algo como:
    # from playwright.sync_api import sync_playwright
    # with sync_playwright() as p:
    #     browser = p.chromium.launch()
    #     page = browser.new_page()
    #     page.goto(url_sitio)
    #     page.fill('input[name="email"]', email_contacto)
    #     page.fill('textarea[name="message"]', mensaje)
    #     page.click('button[type="submit"]')

    return {"status": "simulado", "formulario_id": str(uuid.uuid4())}


# ---------------------------------------------------------------------------
# Función pública principal
# ---------------------------------------------------------------------------

def enviar_micro_sondeo(
    lead_id:        str,
    canal:          CanalContacto,
    destinatario:   str,          # Email o teléfono según el canal
    sitio_web:      Optional[str],
    mensaje:        str,
    nombre_negocio: str,
) -> ResultadoEnvio:
    """
    Envía el micro-sondeo al lead por el canal asignado y registra
    el costo exacto del envío.

    Parámetros:
        lead_id:        ID del lead en la base de datos
        canal:          Canal de contacto (email, whatsapp, formulario_web)
        destinatario:   Email o número de teléfono del prospecto
        sitio_web:      URL del sitio web (para formulario web)
        mensaje:        Texto del micro-sondeo generado por el RAG
        nombre_negocio: Nombre de la pyme (para los logs)

    Retorna:
        ResultadoEnvio con costos y estado del envío
    """
    costos = COSTOS_CANAL.get(canal.value, {"costo_envio": 0.0, "costo_scraping": 0.0})
    costo_envio = costos["costo_envio"]

    if canal == CanalContacto.EMAIL:
        resultado_raw = _enviar_email_simulado(
            destinatario=destinatario,
            asunto=f"Consulta rápida del sector — {nombre_negocio}",
            cuerpo=mensaje,
        )
    elif canal == CanalContacto.WHATSAPP:
        resultado_raw = _enviar_whatsapp_simulado(
            numero=destinatario,
            mensaje=mensaje,
        )
    elif canal == CanalContacto.FORMULARIO_WEB:
        resultado_raw = _enviar_formulario_web_simulado(
            url_sitio=sitio_web or destinatario,
            mensaje=mensaje,
        )
    else:
        resultado_raw = {"status": "canal_no_soportado"}

    exito = resultado_raw.get("status") in ["simulado", "enviado", "ok"]

    resultado = ResultadoEnvio(
        exito            = exito,
        canal            = canal.value,
        costo_envio_usd  = costo_envio,
        costo_tokens_usd = COSTO_TOKENS_LLM_POR_LEAD,  # Generación del mensaje
        mensaje_enviado  = mensaje,
        detalle          = str(resultado_raw),
    )

    _log_seguro(
        f"[CONTACTO] Lead '{nombre_negocio}' contactado por {canal.value}. "
        f"Costo: ${resultado.costo_total_usd:.4f} USD. Éxito: {exito}"
    )

    return resultado


def enviar_propuesta(
    lead_id:        str,
    canal:          CanalContacto,
    destinatario:   str,
    sitio_web:      Optional[str],
    propuesta:      str,
    nombre_negocio: str,
) -> ResultadoEnvio:
    """
    Envía la propuesta personalizada tras recibir respuesta del sondeo.
    Mismo mecanismo que el micro-sondeo pero con el mensaje de propuesta.
    """
    return enviar_micro_sondeo(
        lead_id        = lead_id,
        canal          = canal,
        destinatario   = destinatario,
        sitio_web      = sitio_web,
        mensaje        = propuesta,
        nombre_negocio = nombre_negocio,
    )
