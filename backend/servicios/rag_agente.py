"""
servicios/rag_agente.py — Motor RAG para micro-sondeos y propuestas personalizadas
====================================================================================
Implementa el cerebro inteligente de la plataforma:

1. SELECCIÓN DE MICRO-SONDEO: dado el sector y señal de dolor de un lead,
   selecciona la pregunta de 1 clic más relevante usando matching semántico
   con el catálogo de soluciones Dapta.

2. GENERACIÓN DE PROPUESTA: tras recibir la respuesta del prospecto (opción A/B),
   genera una propuesta personalizada respaldada por casos de éxito reales.

NOTA DEMO: Usa matching por palabras clave + templates inteligentes.
Para producción, descomentar la sección de ChromaDB + LLM real.
"""

import json
import re
import unicodedata
from pathlib import Path
from typing import Optional, Tuple

import httpx

from backend.config import (
    DAPTA_AGENT_ID,
    DAPTA_AGENT_EXECUTE_URL,
)
from backend.modelos.lead import EstadoLead


class DaptaAgentError(RuntimeError):
    """Error al solicitar o interpretar una respuesta del agente Dapta."""


# ---------------------------------------------------------------------------
# Carga del catálogo de soluciones Dapta (base de conocimientos RAG)
# ---------------------------------------------------------------------------

_RUTA_CATALOGO = Path(__file__).parent.parent / "datos_semilla" / "catalogo_dapta.json"

def _cargar_catalogo() -> list[dict]:
    """Carga el catálogo de soluciones desde el JSON semilla."""
    with open(_RUTA_CATALOGO, "r", encoding="utf-8") as f:
        return json.load(f)

_CATALOGO_DAPTA = _cargar_catalogo()


# ---------------------------------------------------------------------------
# Templates de micro-sondeo por tipo de señal de dolor
# ---------------------------------------------------------------------------

_TEMPLATES_SONDEO = {
    "reseña_negativa_atencion": {
        "pregunta": (
            "Hola {nombre_negocio}! Notamos que varios clientes mencionan tiempos de respuesta. "
            "Para un análisis rápido del sector: ¿su mayor cuello de botella es...\n"
            "A) Clientes que preguntan fuera de horario y no reciben respuesta\n"
            "B) Clientes que quedan en espera demasiado tiempo durante el horario\n"
            "Responda solo A o B — tomará 5 segundos 🙏"
        ),
        "opcion_a": "atención_fuera_horario",
        "opcion_b": "esperas_largas_en_horario",
    },
    "reseña_negativa_no_show": {
        "pregunta": (
            "Hola {nombre_negocio}! Vimos comentarios sobre coordinación de citas. "
            "¿Cuál es su mayor problema con reservas?\n"
            "A) Clientes que agendan y no confirman (no-shows)\n"
            "B) Citas que se duplican o chocan en el calendario\n"
            "Responda A o B 👆"
        ),
        "opcion_a": "no_shows",
        "opcion_b": "conflictos_agenda",
    },
    "vacante_ventas_manual": {
        "pregunta": (
            "Hola {nombre_negocio}! Vimos que buscan reforzar su equipo de ventas. "
            "¿Cuál es el cuello de botella actual?\n"
            "A) Los vendedores no dan abasto con el volumen de prospectos\n"
            "B) El seguimiento post-contacto es lento y se pierden oportunidades\n"
            "Solo A o B, gracias ✅"
        ),
        "opcion_a": "volumen_prospectos",
        "opcion_b": "seguimiento_lento",
    },
    "vacante_atencion_cliente": {
        "pregunta": (
            "Hola {nombre_negocio}! Notamos que buscan personal de atención. "
            "¿Dónde se generan más tickets?\n"
            "A) WhatsApp / redes sociales (mensajes que llegan a destiempo)\n"
            "B) Atención telefónica (llamadas que no pueden atender)\n"
            "A o B 📩"
        ),
        "opcion_a": "mensajes_digitales",
        "opcion_b": "llamadas_telefonicas",
    },
    "sin_whatsapp_sitio_lento": {
        "pregunta": (
            "Hola {nombre_negocio}! Revisamos su presencia web y detectamos algunas oportunidades. "
            "¿Cuál cree que les genera más clientes perdidos?\n"
            "A) No tener un canal de contacto inmediato (WhatsApp / chat)\n"
            "B) El sitio web tarda mucho y los clientes se van antes de contactarlos\n"
            "Seleccione A o B 🚀"
        ),
        "opcion_a": "sin_canal_inmediato",
        "opcion_b": "sitio_lento",
    },
    "default": {
        "pregunta": (
            "Hola {nombre_negocio}! Estamos analizando las necesidades de negocios del sector {sector}. "
            "¿Cuál es su mayor reto hoy?\n"
            "A) Conseguir más clientes nuevos\n"
            "B) Atender mejor a los clientes que ya tienen\n"
            "Responda A o B 🙌"
        ),
        "opcion_a": "conseguir_clientes",
        "opcion_b": "mejorar_atencion",
    },
}


# ---------------------------------------------------------------------------
# Matching semántico simplificado (sin ChromaDB para demo)
# ---------------------------------------------------------------------------

def _encontrar_solucion_por_sector_y_dolor(
    sector: str,
    tipo_senal: str,
    opcion_elegida: str,
) -> Optional[dict]:
    """
    Encuentra la solución más relevante del catálogo Dapta para el contexto dado.

    Estrategia de matching:
      1. Filtrar soluciones aplicables al sector del lead
      2. Calcular score de relevancia según el tipo de señal y opción elegida
      3. Retornar la solución con mayor score
    """
    sector_normalizado = sector.lower()

    # Mapa de señales a categorías de solución
    mapa_senal_categoria = {
        "reseña_negativa_atencion": "atencion_cliente",
        "reseña_negativa_no_show":  "atencion_cliente",
        "vacante_ventas_manual":    "ventas_automatizadas",
        "vacante_atencion_cliente": "atencion_cliente",
        "sin_whatsapp_sitio_lento": "presencia_digital",
        "presencia_digital_deficiente": "presencia_digital",
        "reseña_negativa_operaciones": "operaciones",
        "reseña_negativa_seguimiento_ventas": "ventas_automatizadas",
    }
    categoria_buscada = mapa_senal_categoria.get(tipo_senal, "atencion_cliente")

    mejores_candidatos = []
    for solucion in _CATALOGO_DAPTA:
        score = 0

        # +3 puntos si la categoría coincide exactamente
        if solucion["categoria"] == categoria_buscada:
            score += 3

        # +2 puntos si el sector está en la lista de sectores aplicables
        sectores_solucion = solucion.get("sectores_aplicables", [])
        if sector_normalizado in sectores_solucion or "cualquier_sector" in sectores_solucion:
            score += 2

        # +1 punto si el dolor objetivo menciona palabras clave del tipo de señal
        palabras_clave = re.findall(r'\b\w+\b', tipo_senal)
        dolor_objetivo = solucion.get("dolor_objetivo", "").lower()
        for palabra in palabras_clave:
            if palabra in dolor_objetivo:
                score += 1

        if score > 0:
            mejores_candidatos.append((score, solucion))

    if not mejores_candidatos:
        # Fallback: retornar la auditoría web gratuita (siempre relevante)
        return next((s for s in _CATALOGO_DAPTA if s["id"] == "sol-005"), None)

    # Ordenar por score descendente y retornar la mejor
    mejores_candidatos.sort(key=lambda x: x[0], reverse=True)
    return mejores_candidatos[0][1]


def obtener_solucion_para_lead(
    sector: str,
    tipo_senal: str,
    opcion_elegida: str = "A",
) -> Optional[dict]:
    """
    Función pública que expone el matching del catálogo Dapta.
    Usada por el endpoint de auditoría RAG para mostrar qué ficha
    exacta del catálogo fue consultada al generar la propuesta.
    """
    return _encontrar_solucion_por_sector_y_dolor(sector, tipo_senal, opcion_elegida)


# ---------------------------------------------------------------------------
# Funciones públicas del motor RAG
# ---------------------------------------------------------------------------

def seleccionar_micro_sondeo(
    nombre_negocio: str,
    sector:         str,
    tipo_senal:     str,
) -> str:
    """
    Selecciona y formatea el micro-sondeo de 1 pregunta más apropiado
    para el sector y señal de dolor detectada.

    Parámetros:
        nombre_negocio: Nombre de la pyme a contactar
        sector:         Sector del negocio (restaurante, clinica, etc.)
        tipo_senal:     Tipo de señal detectada en el scraper

    Retorna:
        Texto formateado de la pregunta de micro-sondeo lista para enviar.
    """
    template = _TEMPLATES_SONDEO.get(tipo_senal, _TEMPLATES_SONDEO["default"])
    pregunta = template["pregunta"].format(
        nombre_negocio=nombre_negocio,
        sector=sector,
    )
    return pregunta


def generar_propuesta_personalizada(
    nombre_negocio: str,
    sector:         str,
    tipo_senal:     str,
    opcion_elegida: str,  # "A" o "B"
) -> str:
    """
    Genera una propuesta de solución personalizada después de que el
    prospecto respondió el micro-sondeo.

    Usa el catálogo Dapta para personalizar el caso de éxito y los
    beneficios según el sector y dolor específico del lead.

    Parámetros:
        nombre_negocio: Nombre de la pyme
        sector:         Sector del negocio
        tipo_senal:     Tipo de señal de dolor original
        opcion_elegida: La opción que eligió el prospecto ("A" o "B")

    Retorna:
        Texto de propuesta personalizada listo para enviar.
    """
    solucion = _encontrar_solucion_por_sector_y_dolor(sector, tipo_senal, opcion_elegida)

    if not solucion:
        return (
            f"Hola {nombre_negocio}, gracias por responder. "
            "Tenemos una solución de IA que puede ayudarles. "
            "¿Podemos agendar una llamada de 15 minutos esta semana?"
        )

    # Template de propuesta personalizada usando datos del catálogo
    propuesta = (
        f"¡Perfecto {nombre_negocio}! Gracias por responder 🙏\n\n"
        f"Basado en su respuesta, identificamos exactamente el reto que mencionan.\n\n"
        f"💡 **{solucion['titulo']}**\n"
        f"Para negocios del sector {sector}, esto típicamente genera:\n"
        f"✅ {solucion['resultado_tipico']}\n\n"
        f"📋 Caso real: {solucion['caso_exito']}\n\n"
        f"🔧 Implementación en solo {solucion['tiempo_implementacion_dias']} día(s). "
        + (f"Prueba gratuita disponible." if solucion['precio_referencial_usd'] == 0
           else f"Inversión inicial desde ${solucion['precio_referencial_usd']} USD/mes.")
        + f"\n\n¿Les interesa una demo de 15 minutos esta semana? "
        f"Solo responda SÍ y le confirmamos horario 📅"
    )

    return propuesta


def calificar_con_agente_dapta(
    nombre_negocio: str,
    sector: str,
    canal: str = "email",
    senal_dolor: str = "",
    opcion_elegida: Optional[str] = "A",
    propuesta_enviada: bool = True,
    lead_id: Optional[str] = None,
) -> Tuple[str, float, str]:
    """
    Califica al prospecto enviando su información al agente de texto de Dapta
    incluyendo su categoría, nombre de la empresa, canal de contacto y señales
    de dolor.

    Retorna:
        Tupla (estado: str, score_calidad: float, feedback_agente: str)
        donde estado es 'calificado', 'no_calificado' o 'en_revision'.
    """
    categoria = sector or "Pyme / Comercio"

    datos_lead = {
        "empresa": nombre_negocio,
        "categoria": categoria,
        "perfil_cliente": {
            "categoria": categoria,
        },
        "canal_contacto": canal,
        "necesidad_principal": senal_dolor or "No informada",
        "respuesta_microsondeo": opcion_elegida or "Sin respuesta",
        "propuesta_enviada": propuesta_enviada,
        "actividad_en_redes": "No informada",
    }
    mensaje_para_agente = (
        "Al buscar esta empresa, el perfil ideal del cliente que solicita "
        "la calificacion es su sector industrial: "
        f"{categoria}. Usa este perfil para evaluar si la empresa corresponde "
        "al cliente buscado. "
        "Califica este lead utilizando únicamente los datos proporcionados. "
        "Si falta información para decidir, usa "
        "EN_REVISION. Responde incluyendo exactamente uno de estos estados: "
        "ESTADO: CALIFICADO, ESTADO: NO_CALIFICADO o ESTADO: EN_REVISION, "
        "incluye también SCORE: N% como porcentaje entero entre 0% y 100%, "
        "y después explica brevemente el motivo. No omitas el score.\n"
        f"Datos del lead: {json.dumps(datos_lead, ensure_ascii=False)}"
    )

    payload = {
        "message": mensaje_para_agente,
        "channel": "widget",
        "external_id": f"lead-{lead_id or 'eval'}",
    }
    try:
        response = httpx.post(
            DAPTA_AGENT_EXECUTE_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=25.0,
        )
        response.raise_for_status()
        data = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise DaptaAgentError(
            f"No se pudo obtener una calificación del agente Dapta: {exc}"
        ) from exc

    if not isinstance(data, dict):
        raise DaptaAgentError("Dapta devolvió una respuesta con formato inválido.")
    agent_id = data.get("agent_id")
    if agent_id and agent_id != DAPTA_AGENT_ID:
        raise DaptaAgentError(
            f"La respuesta proviene del agente {agent_id}, no del agente configurado."
        )

    output_text = data.get("output")
    if not isinstance(output_text, str) or not output_text.strip():
        raise DaptaAgentError("Dapta no devolvió un veredicto de calificación.")

    estado = _interpretar_veredicto_dapta(output_text, data.get("tool_calls", []))
    score = _extraer_score_dapta(output_text, data)
    if score is None:
        raise DaptaAgentError(
            "Dapta devolvió un veredicto, pero no se encontró un porcentaje "
            "válido en el texto ni en los campos estructurados de la respuesta."
        )
    return estado, score, output_text.strip()


def _normalizar_texto(texto: str) -> str:
    texto_sin_acentos = unicodedata.normalize("NFKD", texto)
    texto_sin_acentos = "".join(
        caracter for caracter in texto_sin_acentos
        if not unicodedata.combining(caracter)
    )
    return re.sub(r"\s+", " ", texto_sin_acentos.lower().replace("_", " ")).strip()


def _interpretar_veredicto_dapta(output_text: str, tool_calls: object) -> str:
    texto = _normalizar_texto(output_text)

    estado_explicito = re.search(
        r"\bestado\s*[:=]\s*(en\s+revision|no\s+calificad[oa]s?|calificad[oa]s?)\b",
        texto,
    )
    if estado_explicito:
        etiqueta = estado_explicito.group(1)
        if etiqueta.startswith("no "):
            return EstadoLead.NO_CALIFICADO.value
        if etiqueta.startswith("en "):
            return EstadoLead.EN_REVISION.value
        return EstadoLead.CALIFICADO.value

    if re.search(
        r"\bno\s+(?:esta\s+)?calificad[oa]s?\b|\bno\s+califica\b|"
        r"\bno\s+cumple(?:n)?(?:\s+con)?\b|\brechazad[oa]s?\b",
        texto,
    ):
        return EstadoLead.NO_CALIFICADO.value

    if re.search(
        r"\bestado\s*[:=]\s*en\s+revision\b|\ben\s+revision\b|"
        r"\bpendiente\b|\binformacion adicional\b|\bdatos insuficientes\b|"
        r"\bfaltan datos\b|\bno se puede determinar\b|\bsin informacion suficiente\b|"
        r"\bneed more information\b|\bunresolved\b",
        texto,
    ):
        return EstadoLead.EN_REVISION.value

    if isinstance(tool_calls, list):
        razones = []
        for llamada in tool_calls:
            if not isinstance(llamada, dict) or not isinstance(llamada.get("args"), dict):
                continue
            razon = llamada["args"].get("reason")
            if isinstance(razon, str):
                razones.append(_normalizar_texto(razon))
        razon_cierre = " ".join(razones)
        if (
            "lead qualification completed" in razon_cierre
            or "calificacion completada" in razon_cierre
        ):
            return EstadoLead.CALIFICADO.value

    if re.search(
        r"\bestado\s*[:=]\s*calificad[oa]s?\b|\bcalificad[oa]s?\b|"
        r"\bcumple[n]?(?:\s+con)?\s+(?:los\s+)?criterios\b|\baprobad[oa]s?\b",
        texto,
    ):
        return EstadoLead.CALIFICADO.value

    return EstadoLead.EN_REVISION.value


def _normalizar_score(valor: object, es_porcentaje: bool = False) -> Optional[float]:
    if isinstance(valor, str):
        coincidencia = re.fullmatch(
            r"\s*(\d+(?:[.,]\d+)?)\s*(%|por\s+ciento|/100|de\s+100|sobre\s+100)?\s*",
            _normalizar_texto(valor),
        )
        if not coincidencia:
            return None
        numero = float(coincidencia.group(1).replace(",", "."))
        es_porcentaje = es_porcentaje or coincidencia.group(2) is not None
    elif isinstance(valor, (int, float)) and not isinstance(valor, bool):
        numero = float(valor)
    else:
        return None

    if es_porcentaje or numero > 1:
        numero /= 100
    return numero if 0 <= numero <= 1 else None


def _extraer_score_dapta(
    output_text: str,
    respuesta_agente: Optional[dict] = None,
) -> Optional[float]:
    if respuesta_agente:
        campos_porcentaje = (
            "score_porcentaje",
            "score_percentage",
            "percentage",
            "porcentaje",
            "calificacion_porcentaje",
        )
        campos_score = ("score", "quality_score", "calificacion")
        for nombre_campo in campos_porcentaje + campos_score:
            valor = respuesta_agente.get(nombre_campo)
            if valor is not None:
                score = _normalizar_score(
                    valor,
                    es_porcentaje=nombre_campo in campos_porcentaje,
                )
                if score is not None:
                    return score

    texto = _normalizar_texto(output_text)
    etiquetas_score = (
        r"(?:score|puntaje|puntuacion|porcentaje|calificacion)"
        r"(?:\s+de\s+calidad)?"
    )
    expresiones = (
        rf"\b{etiquetas_score}\s*(?:[:=]|\bes\b)?\s*"
        r"(\d+(?:[.,]\d+)?)\s*(%|por\s+ciento|/100|de\s+100|sobre\s+100)?",
        r"\b(\d+(?:[.,]\d+)?)\s*(%|por\s+ciento)",
    )
    candidatos: list[float] = []
    for expresion in expresiones:
        for coincidencia in re.finditer(expresion, texto):
            numero = float(coincidencia.group(1).replace(",", "."))
            marcador_porcentaje = coincidencia.group(2) is not None
            score = _normalizar_score(numero, es_porcentaje=marcador_porcentaje)
            if score is not None:
                candidatos.append(score)

    return candidatos[0] if candidatos else None
