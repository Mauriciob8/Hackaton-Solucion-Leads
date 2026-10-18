"""
config.py — Configuración central del Motor de Leads
=====================================================
Centraliza todas las variables de entorno, constantes del sistema y
costos operativos por canal. Usar os.environ.get() permite sobrescribir
cualquier valor sin tocar el código fuente (ideal para producción).
"""

import os

# ---------------------------------------------------------------------------
# Servidor
# ---------------------------------------------------------------------------
HOST = os.environ.get("HOST", "0.0.0.0")
PUERTO = int(os.environ.get("PUERTO", 8000))
MODO_DEBUG = os.environ.get("MODO_DEBUG", "true").lower() == "true"

# ---------------------------------------------------------------------------
# Base de datos
# ---------------------------------------------------------------------------
# En producción se puede cambiar a postgresql://...
RUTA_BASE_DATOS = os.environ.get(
    "RUTA_BASE_DATOS",
    "motor_leads.db"
)
FRONTEND_URL = os.environ.get("FRONTEND_URL", "").strip()

# ---------------------------------------------------------------------------
# Costos operativos por canal (en USD)
# Fuente de los valores:
#   - Email:     Resend / Amazon SES  → ~$0.0002 por envío
#   - WhatsApp:  Cloud API (Tier 1)   → ~$0.0350 por conversación
#   - Formulario web: sin costo de envío directo
# ---------------------------------------------------------------------------
COSTOS_CANAL = {
    "email": {
        "costo_envio": float(os.environ.get("COSTO_EMAIL", 0.0002)),
        "costo_scraping": float(os.environ.get("COSTO_SCRAPING_EMAIL", 0.0001)),
    },
    "whatsapp": {
        "costo_envio": float(os.environ.get("COSTO_WHATSAPP", 0.0350)),
        "costo_scraping": float(os.environ.get("COSTO_SCRAPING_WA", 0.0001)),
    },
    "formulario_web": {
        "costo_envio": float(os.environ.get("COSTO_FORMULARIO", 0.0000)),
        "costo_scraping": float(os.environ.get("COSTO_SCRAPING_WEB", 0.0001)),
    },
}

# Costo promedio de tokens LLM por lead (GPT-4o-mini / Claude Haiku)
# ~500 tokens de entrada + ~300 salida, ~$0.0003 por análisis
COSTO_TOKENS_LLM_POR_LEAD = float(os.environ.get("COSTO_TOKENS_LLM", 0.0003))

# ---------------------------------------------------------------------------
# API Keys opcionales (para conectar LLM real en producción)
# ---------------------------------------------------------------------------
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# Modelo LLM a usar (si se configuró una key)
MODELO_LLM = os.environ.get("MODELO_LLM", "gpt-4o-mini")

# ---------------------------------------------------------------------------
# Agente de Texto Dapta (Calificador Real)
# ---------------------------------------------------------------------------
DAPTA_AGENT_ID = os.environ.get(
    "DAPTA_AGENT_ID",
    "a2f51962-1754-4ff4-a5d3-0082625607cc"
)
DAPTA_AGENT_EXECUTE_URL = os.environ.get(
    "DAPTA_AGENT_EXECUTE_URL",
    f"https://agents-v2.dapta.ai/text-agent-v2/api/v2/agents/{DAPTA_AGENT_ID}/execute"
)
DAPTA_TIMEOUT_SECONDS = float(os.environ.get("DAPTA_TIMEOUT_SECONDS", "90"))

# ---------------------------------------------------------------------------
# Límites operativos
# ---------------------------------------------------------------------------
MAX_LEADS_POR_CAMPANA = int(os.environ.get("MAX_LEADS_POR_CAMPANA", 500))
PAGINA_TAMANO_DEFAULT = int(os.environ.get("PAGINA_TAMANO_DEFAULT", 20))
