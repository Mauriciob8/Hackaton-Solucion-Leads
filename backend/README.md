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
  DAPTA_AGENT_ID=a2f51962-1754-4ff4-a5d3-0082625607cc
  DAPTA_AGENT_EXECUTE_URL=https://agents-v2.dapta.ai/text-agent-v2/api/v2/agents/a2f51962-1754-4ff4-a5d3-0082625607cc/execute

La calificación del pipeline consulta este agente en cada solicitud. Si Dapta
no responde, la API devuelve un error y no inventa ni persiste un veredicto.
La categoría del lead se incluye en los datos enviados al agente y se declara
explícitamente como el perfil del cliente a calificar; no se solicita ingreso
mensual ni esfuerzo. Además, se envía como la variable `perfil_cliente` y
dentro de `variables.datos_lead`. El estado persistido en el pipeline
corresponde al veredicto devuelto. Si Dapta devuelve `EN_REVISION` con un
score de 74% o superior, el pipeline marca el lead como `calificado`.
La respuesta de calificación debe incluir `SCORE: N%` (0 a 100). El backend
guarda el score como fracción de 0 a 1 en `score_calidad_dapta` y la API
también devuelve `score_calidad_porcentaje` para expresar el valor de 0 a 100.
Si falta un score válido, no se guarda el resultado y la API informa un error.

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
