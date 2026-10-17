backend/README.md — Motor de Leads
===================================

ARRANQUE RÁPIDO
---------------
Desde la raíz del proyecto (motor-leads-hackaton/):

  pip install fastapi uvicorn pydantic
  uvicorn backend.main:app --reload --port 8000

Documentación interactiva: http://localhost:8000/docs

VARIABLES DE ENTORNO (opcionales)
----------------------------------
  RUTA_BASE_DATOS=motor_leads.db     # Ruta al archivo SQLite
  COSTO_EMAIL=0.0002                 # Costo por email en USD
  COSTO_WHATSAPP=0.0350              # Costo por mensaje WhatsApp en USD
  OPENAI_API_KEY=sk-...              # Para conectar LLM real (opcional)
  MODO_SIMULACION_DAPTA=true         # false = webhook real a Dapta

ESTRUCTURA
----------
  backend/
    config.py          Configuración central (costos, variables de entorno)
    main.py            Punto de entrada FastAPI
    modelos/           Dataclasses: Lead, EventoCosto, MetricaCanal
    servicios/         Lógica: scraper, RAG, contacto, métricas
    rutas/             Endpoints: /api/leads, /api/campanas, /api/metricas
    base_datos/        SQLite con SQLAlchemy Core
    datos_semilla/     Catálogo JSON de soluciones Dapta para RAG
