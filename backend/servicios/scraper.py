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
# Base de datos semilla: 50 pymes con señales de dolor reales (Benchmark Hackathon)
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
        "sitio_web": "ferreteriadonjaime.co",
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
    {
        "nombre_negocio": "Hotel Boutique Casa Colonial",
        "sector": "hoteleria",
        "ciudad": "Cartagena",
        "telefono": "+57 312 555 2525",
        "senal_dolor": "Reseña pública: 'Intenté reservar habitación para aniversario por WhatsApp y contestaron al día siguiente cuando ya no había disponibilidad.'",
        "tipo_senal": "reseña_negativa_atencion",
        "email": "reservas@hotelcasacolonial.co",
        "sitio_web": "hotelcasacolonial.co",
    },
    {
        "nombre_negocio": "Centro Oftalmológico Visión Clara",
        "sector": "clinica",
        "ciudad": "Medellín",
        "telefono": "+57 313 555 2626",
        "senal_dolor": "Reseña pública: 'Pido cotización de cirugía refractiva por chat y el enlace de citas siempre da error sin seguimiento de nadie.'",
        "tipo_senal": "reseña_negativa_no_show",
        "email": "citas@visionclaramed.com",
        "sitio_web": "visionclaramed.com",
    },
    {
        "nombre_negocio": "Autoescuela Conduzca Seguro",
        "sector": "educacion",
        "ciudad": "Bogotá",
        "telefono": "+57 314 555 2727",
        "senal_dolor": "Reseña pública: 'Nadie atiende el teléfono ni responden los mensajes de WhatsApp para programar clases prácticas de conducción.'",
        "tipo_senal": "reseña_negativa_atencion",
        "email": "contacto@conduzcaseguro.co",
        "sitio_web": "conduzcaseguro.co",
    },
    {
        "nombre_negocio": "Distribuidora Eléctrica Andina",
        "sector": "comercio",
        "ciudad": "Cali",
        "telefono": "+57 315 555 2828",
        "senal_dolor": "Reseña pública: 'Muy buenos insumos pero tardan horas en cotizar pedidos industriales por WhatsApp. Se van los clientes.'",
        "tipo_senal": "reseña_negativa_atencion",
        "email": "ventas@electricaandina.com.co",
        "sitio_web": "electricaandina.com.co",
    },
    {
        "nombre_negocio": "Spa & Bienestar Armonía Natural",
        "sector": "bienestar",
        "ciudad": "Pereira",
        "telefono": "+57 316 555 2929",
        "senal_dolor": "Reseña pública: 'Me confirmaron un masaje en pareja por mensaje y al llegar a la sede no tenían anotada la reserva en recepción.'",
        "tipo_senal": "reseña_negativa_no_show",
        "email": "recepcion@armonianaturalspa.co",
        "sitio_web": "armonianaturalspa.co",
    },
    {
        "nombre_negocio": "Lavandería Industrial CleanExpress",
        "sector": "servicios",
        "ciudad": "Manizales",
        "telefono": "+57 317 555 3030",
        "senal_dolor": "Reseña pública: 'Imposible saber el estado de entrega de los uniformes corporativos; no responden mensajes durante todo el fin de semana.'",
        "tipo_senal": "reseña_negativa_operaciones",
        "email": "operaciones@cleanexpress.com.co",
        "sitio_web": "cleanexpress.com.co",
    },
    {
        "nombre_negocio": "Tienda de Mascotas Guau & Miau",
        "sector": "comercio",
        "ciudad": "Barranquilla",
        "telefono": "+57 318 555 3131",
        "senal_dolor": "Reseña pública: 'Prometen entrega de concentrado el mismo día por WhatsApp pero nunca envían número de guía ni confirmación.'",
        "tipo_senal": "reseña_negativa_atencion",
        "email": "pedidos@guauymiau.co",
        "sitio_web": "guauymiau.co",
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
    {
        "nombre_negocio": "Concesionario Motos del Valle",
        "sector": "comercio",
        "ciudad": "Cali",
        "telefono": "+57 311 555 3232",
        "senal_dolor": "Vacante: 'Asesor comercial para responder solicitudes entrantes por WhatsApp y agendar test-drives manualmente en libreta.'",
        "tipo_senal": "vacante_ventas_manual",
        "email": "ventas@motosdelvalle.com.co",
        "sitio_web": "motosdelvalle.com.co",
    },
    {
        "nombre_negocio": "Confecciones & Textiles Antillana",
        "sector": "textil",
        "ciudad": "Barranquilla",
        "telefono": "+57 312 555 3333",
        "senal_dolor": "Vacante: 'Auxiliar comercial para tomar pedidos de catálogos mayoristas vía chat y digitar cotizaciones a mano.'",
        "tipo_senal": "vacante_ventas_manual",
        "email": "comercial@textilesantillana.co",
        "sitio_web": "textilesantillana.co",
    },
    {
        "nombre_negocio": "Agencia Digital Impulso Pyme",
        "sector": "marketing",
        "ciudad": "Bogotá",
        "telefono": "+57 313 555 3434",
        "senal_dolor": "Vacante: 'Ejecutivo de cuentas para seguimiento manual de leads en frío y agendamiento de videollamadas comerciales.'",
        "tipo_senal": "vacante_ventas_manual",
        "email": "talento@impulsopyme.co",
        "sitio_web": "impulsopyme.co",
    },
    {
        "nombre_negocio": "Laboratorio Clínico VidaLab",
        "sector": "salud",
        "ciudad": "Bucaramanga",
        "telefono": "+57 314 555 3535",
        "senal_dolor": "Vacante: 'Recepcionista para enviar resultados de exámenes médicos por PDF a través de WhatsApp manualmente uno a uno.'",
        "tipo_senal": "vacante_atencion_cliente",
        "email": "contacto@vidalab.com.co",
        "sitio_web": "vidalab.com.co",
    },
    {
        "nombre_negocio": "Distribuidora Farmacéutica del Caribe",
        "sector": "farmacia",
        "ciudad": "Cartagena",
        "telefono": "+57 315 555 3636",
        "senal_dolor": "Vacante: 'Asistente de despacho para responder consultas de stock a farmacias por mensajes de texto durante la jornada.'",
        "tipo_senal": "vacante_atencion_cliente",
        "email": "despachos@farmadelcaribe.co",
        "sitio_web": "farmadelcaribe.co",
    },
    {
        "nombre_negocio": "Seguridad Privada Vigilantes Unidos",
        "sector": "servicios",
        "ciudad": "Pereira",
        "telefono": "+57 316 555 3737",
        "senal_dolor": "Vacante: 'Coordinador de operaciones para atender requerimientos de clientes y reportar novedades de guardias por chat.'",
        "tipo_senal": "vacante_atencion_cliente",
        "email": "rrhh@vigilantesunidos.co",
        "sitio_web": "vigilantesunidos.co",
    },
    {
        "nombre_negocio": "Instituto de Idiomas GlobalSpeak",
        "sector": "educacion",
        "ciudad": "Medellín",
        "telefono": "+57 317 555 3838",
        "senal_dolor": "Vacante: 'Asesor educativo para contactar aspirantes que dejaron datos en formularios web y clasificar su nivel de inglés.'",
        "tipo_senal": "vacante_ventas_manual",
        "email": "matriculas@globalspeak.edu.co",
        "sitio_web": "globalspeak.edu.co",
    },
    {
        "nombre_negocio": "Cooperativa Financiera CooProgreso",
        "sector": "finanzas",
        "ciudad": "Manizales",
        "telefono": "+57 318 555 3939",
        "senal_dolor": "Vacante: 'Asesor de créditos para solicitar documentos a solicitantes por WhatsApp y digitar estados en Excel.'",
        "tipo_senal": "vacante_ventas_manual",
        "email": "creditos@cooprogreso.co",
        "sitio_web": "cooprogreso.co",
    },
    {
        "nombre_negocio": "Mudanzas y Cargas Nacionales",
        "sector": "transporte",
        "ciudad": "Bogotá",
        "telefono": "+57 319 555 4040",
        "senal_dolor": "Vacante: 'Cotizador telefónico para calcular tarifas de fletes y responder solicitudes de cotización una a una.'",
        "tipo_senal": "vacante_ventas_manual",
        "email": "cotizaciones@cargasnacionales.com",
        "sitio_web": "cargasnacionales.com",
    },
    {
        "nombre_negocio": "Frigorífico & Alimentos El Corral",
        "sector": "alimentos",
        "ciudad": "Cali",
        "telefono": "+57 310 555 4141",
        "senal_dolor": "Vacante: 'Asistente de ventas para consolidar pedidos de carnicerías y restaurantes mediante mensajes de texto.'",
        "tipo_senal": "vacante_ventas_manual",
        "email": "pedidos@frigorificoelcorral.co",
        "sitio_web": "frigorificoelcorral.co",
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
    {
        "nombre_negocio": "Consultores Contables & Tributarios Asesores",
        "sector": "servicios_profesionales",
        "ciudad": "Bogotá",
        "telefono": "+57 311 555 4242",
        "senal_dolor": "Auditoría web: Sitio sin llamada a la acción clara, formulario de contacto sin validación de envío y sin chat directo.",
        "tipo_senal": "sin_whatsapp_sitio_lento",
        "email": "contacto@contablesasesores.co",
        "sitio_web": "contablesasesores.co",
    },
    {
        "nombre_negocio": "Centro de Fisioterapia Activa",
        "sector": "salud",
        "ciudad": "Medellín",
        "telefono": "+57 312 555 4343",
        "senal_dolor": "Auditoría web: Página tarda 7.8s en responder en móvil, botón de agendamiento desconfigurado que no abre WhatsApp.",
        "tipo_senal": "sin_whatsapp_sitio_lento",
        "email": "citas@fisioterapiaactiva.com",
        "sitio_web": "fisioterapiaactiva.com",
    },
    {
        "nombre_negocio": "Eventos y Catering Delicias Gourmet",
        "sector": "eventos",
        "ciudad": "Cartagena",
        "telefono": "+57 313 555 4444",
        "senal_dolor": "Auditoría web: Catálogo de menús en PDF desactualizado de 20MB que bloquea navegadores móviles, sin opción de cotizar en línea.",
        "tipo_senal": "presencia_digital_deficiente",
        "email": "eventos@deliciasgourmet.co",
        "sitio_web": "deliciasgourmet.co",
    },
    {
        "nombre_negocio": "Muebles & Diseños Contemporáneos",
        "sector": "muebles",
        "ciudad": "Bucaramanga",
        "telefono": "+57 314 555 4545",
        "senal_dolor": "Auditoría web: Sitio web desarrollado en tecnología obsoleta, enlaces de redes sociales rotos y sin formulario de contacto.",
        "tipo_senal": "presencia_digital_deficiente",
        "email": "ventas@mueblescontemporaneos.co",
        "sitio_web": "mueblescontemporaneos.co",
    },
    {
        "nombre_negocio": "Empresa de Aseo y Mantenimiento LimpioYa",
        "sector": "servicios",
        "ciudad": "Cali",
        "telefono": "+57 315 555 4646",
        "senal_dolor": "Auditoría web: Sin certificado de seguridad HTTPS, sin botón de WhatsApp, formulario envía a buzón desatendido.",
        "tipo_senal": "presencia_digital_deficiente",
        "email": "contacto@limpioya.com.co",
        "sitio_web": "limpioya.com.co",
    },
    {
        "nombre_negocio": "Joyería y Accesorios Filigrana Real",
        "sector": "joyeria",
        "ciudad": "Barranquilla",
        "telefono": "+57 316 555 4747",
        "senal_dolor": "Auditoría web: Sitio de comercio electrónico sin pasarela de pagos activa y sin canal de asistencia por chat para compras.",
        "tipo_senal": "sin_whatsapp_sitio_lento",
        "email": "ventas@filigranareal.com",
        "sitio_web": "filigranareal.com",
    },
    {
        "nombre_negocio": "Inversiones Inmobiliarias Sol & Playa",
        "sector": "inmobiliaria",
        "ciudad": "Cartagena",
        "telefono": "+57 317 555 4848",
        "senal_dolor": "Auditoría web: Portal inmobiliario sin buscador por precio ni botón de WhatsApp para coordinar visitas a propiedades.",
        "tipo_senal": "presencia_digital_deficiente",
        "email": "info@solyplayainmobiliaria.co",
        "sitio_web": "solyplayainmobiliaria.co",
    },
    {
        "nombre_negocio": "Hospital Veterinario 24 Horas San Francisco",
        "sector": "veterinaria",
        "ciudad": "Pereira",
        "telefono": "+57 318 555 4949",
        "senal_dolor": "Auditoría web: Sitio web sin número de urgencias visible en cabecera móvil, tarda más de 8 segundos en cargar.",
        "tipo_senal": "sin_whatsapp_sitio_lento",
        "email": "urgencias@veterinariasanfrancisco.co",
        "sitio_web": "veterinariasanfrancisco.co",
    },
    {
        "nombre_negocio": "Empaques y Cartones de Colombia",
        "sector": "industria",
        "ciudad": "Manizales",
        "telefono": "+57 319 555 5050",
        "senal_dolor": "Auditoría web: Sitio institucional sin catálogo de productos interactivo, formulario de contacto muestra error 500 al enviar.",
        "tipo_senal": "presencia_digital_deficiente",
        "email": "ventas@empaquescolombia.co",
        "sitio_web": "empaquescolombia.co",
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
    detectados con señales de dolor reales. Prioriza prospectos que no hayan
    sido registrados previamente en la base de datos para evitar duplicados.

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

    # Combinar todas las fuentes de pymes (50 empresas en total)
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

    # Consultar nombres existentes en base de datos para priorizar nuevos
    try:
        from backend.base_datos.conexion import obtener_nombres_leads_existentes
        nombres_existentes = obtener_nombres_leads_existentes()
    except Exception:
        nombres_existentes = set()

    # Separar en nuevos (no registrados) y ya registrados
    pymes_nuevas = [
        item for item in todas_las_pymes
        if (item[0]["nombre_negocio"] or "").strip().lower() not in nombres_existentes
    ]
    pymes_existentes = [
        item for item in todas_las_pymes
        if (item[0]["nombre_negocio"] or "").strip().lower() in nombres_existentes
    ]

    random.shuffle(pymes_nuevas)
    random.shuffle(pymes_existentes)

    # Priorizar leads nuevos; si faltan para la cuota, agregar de los existentes
    seleccionadas = (pymes_nuevas + pymes_existentes)[:cantidad_maxima]

    leads_detectados = []
    costo_scraping_base = COSTOS_CANAL.get(canal_preferido.value, {}).get("costo_scraping", 0.0001)

    for pyme_data, fuente in seleccionadas:
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
            costo_tokens     = COSTO_TOKENS_LLM_POR_LEAD,
            fecha_deteccion  = fecha_deteccion,
        )
        leads_detectados.append(lead)

    print(f"[SCRAPER] {len(leads_detectados)} leads detectados (canal: {canal_preferido.value})")
    return leads_detectados
