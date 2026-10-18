"""
main.py — Punto de entrada principal de la API Motor de Leads
=============================================================
Inicializa FastAPI con todos los routers modulares y la base de datos SQLite.

Para arrancar:
  uvicorn backend.main:app --reload --port 8000

Endpoints disponibles:
  GET  /                          → Health check
  GET  /docs                      → Documentación Swagger UI
  GET  /api/metricas              → CPL por canal (compatible frontend)
  GET  /api/metricas/cpl          → CPL detallado
  GET  /api/metricas/funnel       → Funnel de conversión
  GET  /api/metricas/resumen      → KPIs globales
  GET  /api/leads                 → Listar leads
  POST /api/leads/detectar        → Detectar nuevos leads
  GET  /api/leads/{id}            → Detalle de lead
  POST /api/leads/{id}/contactar  → Enviar micro-sondeo
  POST /api/leads/{id}/respuesta  → Registrar respuesta
  POST /api/leads/{id}/calificar  → Calificar con Dapta
  GET  /api/campanas              → Listar campañas
  POST /api/campanas              → Crear campaña
"""

import sys

# Configurar salida estándar en UTF-8 para compatibilidad en Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.base_datos.conexion import inicializar_base_datos
from backend.config import FRONTEND_URL
from backend.rutas import router_leads, router_campanas, router_metricas


def _normalizar_origen(origen: str) -> str:
    origen = origen.strip().rstrip("/")
    if origen and "://" not in origen:
        origen = f"https://{origen}"
    return origen


# ---------------------------------------------------------------------------
# Instancia de la aplicación
# ---------------------------------------------------------------------------

app = FastAPI(
    title       = "Motor de Leads — Intent-Based Lead Engine",
    description = (
        "Plataforma que detecta pymes con señales de dolor reales en fuentes gratuitas, "
        "las contacta con micro-sondeos de 1 pregunta y mide el CPL Bruto vs. Calificado "
        "por canal para optimizar el costo de adquisición de leads."
    ),
    version     = "1.0.0",
    docs_url    = "/docs",
    redoc_url   = "/redoc",
)


# ---------------------------------------------------------------------------
# Middleware CORS — permite conexión con el frontend Next.js
# ---------------------------------------------------------------------------

origenes_permitidos = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
if FRONTEND_URL:
    origen_frontend = _normalizar_origen(FRONTEND_URL)
    if origen_frontend not in origenes_permitidos:
        origenes_permitidos.append(origen_frontend)

app.add_middleware(
    CORSMiddleware,
    allow_origins     = origenes_permitidos,
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)


# ---------------------------------------------------------------------------
# Evento de arranque: inicializar la base de datos
# ---------------------------------------------------------------------------

@app.on_event("startup")
def al_arrancar():
    """Crea las tablas SQLite si no existen al iniciar el servidor."""
    inicializar_base_datos()
    print("[MOTOR DE LEADS] Backend FastAPI iniciado correctamente ✅")
    print("[MOTOR DE LEADS] Documentación disponible en: http://localhost:8000/docs")


# ---------------------------------------------------------------------------
# Registrar routers modulares
# ---------------------------------------------------------------------------

app.include_router(router_leads)
app.include_router(router_campanas)
app.include_router(router_metricas)


# ---------------------------------------------------------------------------
# Endpoint raíz — Health check
# ---------------------------------------------------------------------------

@app.get("/", tags=["Sistema"], summary="Health check del servidor")
def inicio():
    """Verifica que el backend está funcionando correctamente."""
    return {
        "status":    "operativo",
        "servicio":  "Motor de Leads — Lead Engine API",
        "version":   "1.0.0",
        "endpoints": {
            "documentacion":  "/docs",
            "metricas":       "/api/metricas",
            "leads":          "/api/leads",
            "campanas":       "/api/campanas",
        },
    }