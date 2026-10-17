"""
servicios/scraper.py — Scraper de señales de dolor en fuentes gratuitas
========================================================================
Detecta pymes con necesidades reales a partir de señales públicas, en lugar
de raspar listas ciegas. Esto garantiza que el primer contacto sea relevante.

Fuentes simuladas (con estructura lista para conectar APIs reales):
  1. Google Maps — Reseñas con quejas de atención lenta o sin respuesta
  2. Portales de Empleo — Empresas buscando vendedores o atención al cliente
  3. Auditoría Web — Sitios sin botón WhatsApp o con carga lenta

NOTA DEMO: Los datos son pymes realistas de muestra. Para producción,
conectar la API de Google Places + SerpAPI para datos reales.
"""

import random
import uuid
from datetime import datetime, timedelta
from typing import Optional

from backend.config import COSTOS_CANAL, COSTO_TOKENS_LLM_POR_LEAD
from backend.modelos.lead import (
    Lead, CanalContacto, FuenteDeteccion, EstadoLead
)


# ---------------------------------------------------------------------------
# Base de datos semilla: pymes con señales de dolor reales (demo)
# ---------------------------------------------------------------------------

_PYMES_GOOGLE_MAPS = [
    {
        "nombre_negocio": "Restaurante El Fogón de Abuela",
        "sector": "restaurante",
        "ciudad": "Bogotá",
        "telefono": "+57 310 555 0101",
        "senal_dolor": "Reseña pública: 'Tardaron 20 minutos en responder por WhatsApp para reservar una mesa. Al final fui a otro restaurante.'",
        "tipo_senal": "reseña_negativa_atencion",
        "email": "contacto@fogondeabuela.co",
        "sitio_web": "fogondeabuela.co",
    },
    {
        "nombre_negocio": "Clínica Dental Sonrisa Perfecta",
        "sector": "clinica",
        "ciudad": "Medellín",
        "telefono": "+57 312 555 0202",
        "senal_dolor": "Reseña: 'Agendé cita y no me confirmaron. Llegué y no estaba registrada. Pésima organización.'",
        "tipo_senal": "reseña_negativa_no_show",
        "email": "admin@sonrisaperfecta.com.co",
        "sitio_web": "sonrisaperfecta.com.co",
    },
    {
        "nombre_negocio": "Taller Automotriz Los Mecánicos",
        "sector": "taller",
        "ciudad": "Cali",
        "telefono": "+57 315 555 0303",
        "senal_dolor": "Reseña: 'Pregunto precios por WhatsApp y tardan días en responder. La competencia me responde en minutos.'",
        "tipo_senal": "reseña_negativa_atencion",
        "email": "info@tallerlosmecanicos.co",
        "sitio_web": "tallerlosmecanicos.co",
    },
    {
        "nombre_negocio": "Salón de Belleza Glamour",
        "sector": "salon_belleza",
        "ciudad": "Barranquilla",
        "telefono": "+57 318 555 0404",
        "senal_dolor": "Reseña: 'Me dejaron esperando 30 minutos porque no recordaban mi cita. Necesitan un sistema mejor.'",
        "tipo_senal": "reseña_negativa_no_show",
        "email": "citas@glamoursalon.co",
        "sitio_web": "glamoursalon.co",
    },
    {
        "nombre_negocio": "Ferretería Don Jaime",
        "sector": "comercio",
        "ciudad": "Bucaramanga",
        "telefono": "+57 316 555 0505",
        "senal_dolor": "Reseña: 'Tienen buena mercancía pero nunca tienen lista de precios online. Toca ir en persona.'",
        "tipo_senal": "reseña_negativa_presencia_digital",
        "email": "donjaime@ferreteria.co",
        "sitio_web": "",
    },
    {
        "nombre_negocio": "Veterinaria PetCare",
        "sector": "veterinaria",
        "ciudad": "Bogotá",
        "telefono": "+57 314 555 0606",
        "senal_dolor": "Reseña: 'Imposible saber si tienen cupo en urgencias. No responden a ninguna hora fuera de oficina.'",
        "tipo_senal": "reseña_negativa_atencion",
        "email": "atencion@petcare.com.co",
        "sitio_web": "petcare.com.co",
    },
    {
        "nombre_negocio": "Panadería El Trigal",
        "sector": "panaderia",
        "ciudad": "Pereira",
        "telefono": "+57 317 555 0707",
        "senal_dolor": "Reseña: 'Hago pedidos grandes por WhatsApp y siempre se les olvida algo. Se necesita más organización.'",
        "tipo_senal": "reseña_negativa_operaciones",
        "email": "pedidos@eltrigal.co",
        "sitio_web": "eltrigal.co",
    },
    {
        "nombre_negocio": "Inmobiliaria CasaFácil",
        "sector": "inmobiliaria",
        "ciudad": "Bogotá",
        "telefono": "+57 311 555 0808",
        "senal_dolor": "Reseña: 'Mostré interés en un apartamento y nunca me volvieron a llamar. Terminé comprando con otro agente.'",
        "tipo_senal": "reseña_negativa_seguimiento_ventas",
        "email": "ventas@casafacil.com.co",
        "sitio_web": "casafacil.com.co",
    },
    {
        "nombre_negocio": "Gimnasio Heroica Fitness Club",
        "sector": "gimnasio",
        "ciudad": "Cartagena",
        "telefono": "+57 300 555 1414",
        "senal_dolor": "Reseña pública: 'Pésimo sistema para reservar clases de spinning. Por WhatsApp nunca responden y cuando llego me dicen que no hay cupo.'",
        "tipo_senal": "reseña_negativa_no_show",
        "email": "contacto@heroicafitness.co",
        "sitio_web": "heroicafitness.co",
    },
    {
        "nombre_negocio": "Laboratorio Dental Arte & Sonrisas",
        "sector": "laboratorio_dental",
        "ciudad": "Bogotá",
        "telefono": "+57 301 555 1515",
        "senal_dolor": "Reseña pública: 'Tardan más de dos días en enviar cotizaciones de prótesis a odontólogos. Perdemos pacientes por su demora.'",
        "tipo_senal": "reseña_negativa_atencion",
        "email": "cotizaciones@arteysonrisaslab.com",
        "sitio_web": "arteysonrisaslab.com",
    },
    {
        "nombre_negocio": "Peluquería Canina Pelos y Huellas",
        "sector": "peluqueria_canina",
        "ciudad": "Cali",
        "telefono": "+57 302 555 1616",
        "senal_dolor": "Reseña pública: 'No tienen ningún sistema de agendamiento online ni por WhatsApp. Toca llamar diez veces para conseguir cita de baño.'",
        "tipo_senal": "reseña_negativa_atencion",
        "email": "citas@pelosyhuellas.co",
        "sitio_web": "pelosyhuellas.co",
    },
    {
        "nombre_negocio": "Imprenta y Litografía Costeña",
        "sector": "imprenta",
        "ciudad": "Barranquilla",
        "telefono": "+57 304 555 1717",
        "senal_dolor": "Reseña pública: 'Mandé a imprimir 500 folletos corporativos urgentes y traspapelaron la orden. No tienen control de sus pedidos.'",
        "tipo_senal": "reseña_negativa_operaciones",
        "email": "ordenes@litografiacostena.com",
        "sitio_web": "litografiacostena.com",
    },
    {
        "nombre_negocio": "Bufete Legal Gómez & Restrepo Abogados",
        "sector": "bufete_legal",
        "ciudad": "Medellín",
        "telefono": "+57 305 555 1818",
        "senal_dolor": "Reseña pública: 'Fui para una asesoría laboral, prometieron enviar la propuesta al día siguiente y pasaron semanas sin seguimiento.'",
        "tipo_senal": "reseña_negativa_seguimiento_ventas",
        "email": "casos@gomezrestrepo.co",
        "sitio_web": "gomezrestrepo.co",
    },
    {
        "nombre_negocio": "Agencia de Viajes Destinos & Rutas",
        "sector": "agencia_viajes",
        "ciudad": "Bogotá",
        "telefono": "+57 310 555 1919",
        "senal_dolor": "Reseña pública: 'Compré un paquete vacacional y los vouchers del hotel quedaron sin confirmación hasta horas antes del vuelo por falta de seguimiento.'",
        "tipo_senal": "reseña_negativa_operaciones",
        "email": "reservas@destinosyrutas.com.co",
        "sitio_web": "destinosyrutas.com.co",
    },
    {
        "nombre_negocio": "Farmacia San Nicolás Droguería",
        "sector": "farmacia",
        "ciudad": "Bucaramanga",
        "telefono": "+57 311 555 2020",
        "senal_dolor": "Reseña pública: 'Pedí medicamentos urgentes a domicilio y no hay forma de saber por dónde viene el mensajero ni cuándo llega.'",
        "tipo_senal": "reseña_negativa_atencion",
        "email": "domicilios@farmaciasannicolas.co",
        "sitio_web": "farmaciasannicolas.co",
    },
]

_PYMES_PORTALES_EMPLEO = [
    {
        "nombre_negocio": "Distribuidora TechParts Colombia",
        "sector": "distribucion",
        "ciudad": "Medellín",
        "telefono": "+57 313 555 0909",
        "senal_dolor": "Vacante activa: 'Se busca Asesor Comercial Junior para gestionar clientes por WhatsApp y teléfono. Req: manejo de Google Sheets.' (señal: proceso manual, necesitan automatización)",
        "tipo_senal": "vacante_ventas_manual",
        "email": "rrhh@techparts.com.co",
        "sitio_web": "techparts.com.co",
    },
    {
        "nombre_negocio": "Clínica Óptica Visual Plus",
        "sector": "clinica",
        "ciudad": "Cali",
        "telefono": "+57 319 555 1010",
        "senal_dolor": "Vacante: 'Asistente de Atención al Cliente para responder WhatsApp y agendar citas. Turno partido.' (señal: volumen alto de contactos manuales)",
        "tipo_senal": "vacante_atencion_cliente",
        "email": "contacto@visualplus.co",
        "sitio_web": "visualplus.co",
    },
    {
        "nombre_negocio": "Agencia de Seguros ConfiaSeg",
        "sector": "seguros",
        "ciudad": "Bogotá",
        "telefono": "+57 310 555 1111",
        "senal_dolor": "Vacante: 'Ejecutivo de Ventas Telefónicas para seguimiento de prospectos. Manejo de CRM básico.' (señal: proceso de ventas lento y sin automatización)",
        "tipo_senal": "vacante_ventas_manual",
        "email": "empleo@confiaseg.co",
        "sitio_web": "confiaseg.co",
    },
    {
        "nombre_negocio": "Fintech CreceYa Colombia",
        "sector": "fintech",
        "ciudad": "Bogotá",
        "telefono": "+57 312 555 2121",
        "senal_dolor": "Vacante activa: 'Buscamos Community Manager para responder mensajes directos en Instagram y WhatsApp de forma manual durante todo el día.' (señal: canal de interacción saturado)",
        "tipo_senal": "vacante_atencion_cliente",
        "email": "talento@creceya.co",
        "sitio_web": "creceya.co",
    },
    {
        "nombre_negocio": "Logística Rápida Andina",
        "sector": "logistica",
        "ciudad": "Medellín",
        "telefono": "+57 315 555 2222",
        "senal_dolor": "Vacante: 'Se requiere Asistente de operaciones para actualizar guías de despacho y estados de envíos en hojas de cálculo manuales.' (señal: procesos operativos repetitivos)",
        "tipo_senal": "vacante_ventas_manual",
        "email": "rrhh@rapidaandina.com",
        "sitio_web": "rapidaandina.com",
    },
]

_PYMES_AUDITORIA_WEB = [
    {
        "nombre_negocio": "Papelería y Útiles Don Eduardo",
        "sector": "comercio",
        "ciudad": "Bogotá",
        "telefono": "+57 312 555 1212",
        "senal_dolor": "Auditoría web: Sitio carga en 8.2s (muy lento), sin botón de WhatsApp visible, sin formulario de contacto activo.",
        "tipo_senal": "sin_whatsapp_sitio_lento",
        "email": "doneduardo@papeleria.co",
        "sitio_web": "papeleriadoneduardo.com",
    },
    {
        "nombre_negocio": "Centro de Yoga Equilibrio",
        "sector": "bienestar",
        "ciudad": "Medellín",
        "telefono": "+57 315 555 1313",
        "senal_dolor": "Auditoría web: Sitio sin SSL, formulario de reservas roto (Error 404), sin presencia en Google Maps.",
        "tipo_senal": "presencia_digital_deficiente",
        "email": "info@yogaequilibrio.co",
        "sitio_web": "yogaequilibrio.co",
    },
    {
        "nombre_negocio": "Estudio de Arquitectura Vanguardia",
        "sector": "arquitectura",
        "ciudad": "Cali",
        "telefono": "+57 316 555 2323",
        "senal_dolor": "Auditoría web: Certificado SSL vencido ('Sitio no seguro'), formulario de contacto arroja error y sin botón de WhatsApp.",
        "tipo_senal": "presencia_digital_deficiente",
        "email": "contacto@arquitecturavanguardia.co",
        "sitio_web": "arquitecturavanguardia.co",
    },
    {
        "nombre_negocio": "Academia Musical Armonía",
        "sector": "educacion_musical",
        "ciudad": "Barranquilla",
        "telefono": "+57 317 555 2424",
        "senal_dolor": "Auditoría web: Sitio web tarda 9.4s en cargar, imágenes no optimizadas, sin botón directo de WhatsApp ni catálogo interactivo de clases.",
        "tipo_senal": "sin_whatsapp_sitio_lento",
        "email": "info@academiaarmonia.co",
        "sitio_web": "academiaarmonia.co",
    },
]


# ---------------------------------------------------------------------------
# Función pública: detectar_leads
# ---------------------------------------------------------------------------

def detectar_leads(
    sector:          Optional[str] = None,
    ciudad:          Optional[str] = None,
    canal_preferido: CanalContacto = CanalContacto.EMAIL,
    cantidad_maxima: int           = 20,
) -> list[Lead]:
    """
    Simula el scraping de múltiples fuentes y retorna una lista de leads
    detectados con señales de dolor reales.

    Parámetros:
        sector:          Filtra por sector (ej: "restaurante", "clinica")
        ciudad:          Filtra por ciudad (ej: "Bogotá")
        canal_preferido: Canal de contacto a asignar a los leads
        cantidad_maxima: Límite de leads a retornar

    Retorna:
        Lista de objetos Lead listos para insertar en la base de datos.
    """
    # Normalizar a enum si se recibió como string (ej: "whatsapp")
    if isinstance(canal_preferido, str):
        canal_preferido = CanalContacto(canal_preferido)
    # Combinar todas las fuentes de pymes
    todas_las_pymes = []
    for pyme in _PYMES_GOOGLE_MAPS:
        todas_las_pymes.append((pyme, FuenteDeteccion.GOOGLE_MAPS))
    for pyme in _PYMES_PORTALES_EMPLEO:
        todas_las_pymes.append((pyme, FuenteDeteccion.PORTAL_EMPLEO))
    for pyme in _PYMES_AUDITORIA_WEB:
        todas_las_pymes.append((pyme, FuenteDeteccion.AUDITORIA_WEB))

    # Filtrar por sector y ciudad si se especificaron
    if sector:
        todas_las_pymes = [
            (p, f) for p, f in todas_las_pymes
            if sector.lower() in p["sector"].lower()
        ]
    if ciudad:
        todas_las_pymes = [
            (p, f) for p, f in todas_las_pymes
            if ciudad.lower() in (p.get("ciudad") or "").lower()
        ]

    # Mezclar aleatoriamente para simular resultados frescos
    random.shuffle(todas_las_pymes)
    seleccionadas = todas_las_pymes[:cantidad_maxima]

    leads_detectados = []
    costo_scraping_base = COSTOS_CANAL.get(canal_preferido.value, {}).get("costo_scraping", 0.0001)

    for pyme_data, fuente in seleccionadas:
        # Agregar variación aleatoria a las fechas para simular detección incremental
        dias_atras = random.randint(0, 7)
        fecha_deteccion = datetime.utcnow() - timedelta(days=dias_atras, hours=random.randint(0, 23))

        lead = Lead(
            id               = str(uuid.uuid4()),
            nombre_negocio   = pyme_data["nombre_negocio"],
            sector           = pyme_data["sector"],
            ciudad           = pyme_data.get("ciudad"),
            telefono         = pyme_data.get("telefono"),
            email            = pyme_data.get("email"),
            sitio_web        = pyme_data.get("sitio_web"),
            senal_dolor      = pyme_data["senal_dolor"],
            tipo_senal       = pyme_data["tipo_senal"],
            fuente_deteccion = fuente,
            canal            = canal_preferido,
            estado           = EstadoLead.DETECTADO,
            costo_scraping   = costo_scraping_base,
            costo_tokens     = COSTO_TOKENS_LLM_POR_LEAD,  # Tokens de análisis inicial
            fecha_deteccion  = fecha_deteccion,
        )
        leads_detectados.append(lead)

    print(f"[SCRAPER] {len(leads_detectados)} leads detectados (canal: {canal_preferido.value})")
    return leads_detectados
