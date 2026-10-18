"""
base_datos/conexion.py — Capa de persistencia con SQLite + SQLAlchemy
======================================================================
Usa SQLAlchemy Core (sin ORM) para mantener las dependencias mínimas.
SQLite es suficiente para el hackathon; cambiar a PostgreSQL solo
requiere modificar la URL en config.py.

Tablas:
  - leads          : todos los prospectos detectados
  - eventos_costo  : cada gasto atómico asociado a un lead
  - campanas       : agrupaciones de leads por objetivo
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from backend.config import RUTA_BASE_DATOS


# ---------------------------------------------------------------------------
# Conexión
# ---------------------------------------------------------------------------

def obtener_conexion() -> sqlite3.Connection:
    """
    Devuelve una conexión SQLite con row_factory para acceso por nombre de columna.
    El check_same_thread=False permite uso en FastAPI con múltiples threads.
    """
    conexion = sqlite3.connect(RUTA_BASE_DATOS, check_same_thread=False)
    conexion.row_factory = sqlite3.Row  # Acceso tipo dict a las filas
    conexion.execute("PRAGMA journal_mode=WAL")  # Mejor concurrencia
    return conexion


# ---------------------------------------------------------------------------
# Inicialización del esquema
# ---------------------------------------------------------------------------

ESQUEMA_SQL = """
-- Tabla principal de leads (prospectos detectados)
CREATE TABLE IF NOT EXISTS leads (
    id                  TEXT PRIMARY KEY,
    nombre_negocio      TEXT NOT NULL,
    sector              TEXT NOT NULL,
    ciudad              TEXT,
    telefono            TEXT,
    email               TEXT,
    sitio_web           TEXT,
    senal_dolor         TEXT NOT NULL,
    tipo_senal          TEXT NOT NULL,
    fuente_deteccion    TEXT DEFAULT 'google_maps',
    canal               TEXT DEFAULT 'email',
    estado              TEXT DEFAULT 'detectado',
    pregunta_sondeo     TEXT,
    opcion_respondida   TEXT,
    propuesta_generada  TEXT,
    calificado_dapta    INTEGER DEFAULT 0,
    score_calidad_dapta REAL DEFAULT 0.0,
    feedback_dapta      TEXT,
    costo_scraping      REAL DEFAULT 0.0,
    costo_tokens        REAL DEFAULT 0.0,
    costo_envio         REAL DEFAULT 0.0,
    fecha_deteccion     TEXT NOT NULL,
    fecha_contacto      TEXT,
    fecha_respuesta     TEXT,
    campana_id          TEXT
);

-- Registro atómico de cada gasto operativo
CREATE TABLE IF NOT EXISTS eventos_costo (
    id          TEXT PRIMARY KEY,
    lead_id     TEXT NOT NULL,
    tipo        TEXT NOT NULL,
    monto_usd   REAL NOT NULL,
    descripcion TEXT,
    timestamp   TEXT NOT NULL,
    FOREIGN KEY (lead_id) REFERENCES leads(id)
);

-- Agrupaciones de campaña
CREATE TABLE IF NOT EXISTS campanas (
    id              TEXT PRIMARY KEY,
    nombre          TEXT NOT NULL,
    sector_objetivo TEXT,
    canal           TEXT DEFAULT 'email',
    estado          TEXT DEFAULT 'activa',
    fecha_inicio    TEXT NOT NULL,
    fecha_fin       TEXT
);
"""


def inicializar_base_datos():
    """
    Crea las tablas si no existen. Se llama una vez al arrancar FastAPI.
    Es idempotente: usar IF NOT EXISTS garantiza que no rompe datos existentes.
    """
    conexion = obtener_conexion()
    conexion.executescript(ESQUEMA_SQL)
    # Migración suave de columnas adicionales si la tabla ya existía
    try:
        conexion.execute("ALTER TABLE leads ADD COLUMN feedback_dapta TEXT")
    except Exception:
        pass
    conexion.commit()
    conexion.close()
    print(f"[DB] Base de datos inicializada en: {RUTA_BASE_DATOS}")


# ---------------------------------------------------------------------------
# CRUD de Leads
# ---------------------------------------------------------------------------

def buscar_lead_duplicado(
    nombre_negocio: str,
    telefono: Optional[str] = None,
    email: Optional[str] = None,
) -> Optional[dict]:
    """
    Verifica si ya existe un lead registrado con el mismo nombre de negocio
    o con el mismo teléfono o email de contacto.
    """
    con = obtener_conexion()
    nombre_normalizado = (nombre_negocio or "").strip().lower()
    query = "SELECT * FROM leads WHERE LOWER(TRIM(nombre_negocio)) = ?"
    params: list = [nombre_normalizado]

    tel_limpio = (telefono or "").strip()
    if tel_limpio:
        query += " OR (telefono IS NOT NULL AND TRIM(telefono) != '' AND TRIM(telefono) = ?)"
        params.append(tel_limpio)

    email_limpio = (email or "").strip().lower()
    if email_limpio:
        query += " OR (email IS NOT NULL AND TRIM(email) != '' AND LOWER(TRIM(email)) = ?)"
        params.append(email_limpio)

    fila = con.execute(query, tuple(params)).fetchone()
    con.close()
    return dict(fila) if fila else None


def obtener_nombres_leads_existentes() -> set[str]:
    """Retorna un conjunto con los nombres normalizados de todos los leads ya registrados en la base de datos."""
    con = obtener_conexion()
    filas = con.execute("SELECT LOWER(TRIM(nombre_negocio)) FROM leads").fetchall()
    con.close()
    return {fila[0] for fila in filas if fila[0]}


def insertar_lead(lead_data: dict, permitir_duplicados: bool = False) -> Optional[str]:
    """
    Inserta un lead nuevo en la base de datos.
    Si permitir_duplicados es False y ya existe coincidencia por nombre, teléfono o email,
    omite la inserción y retorna None. Retorna el ID insertado si es exitoso.
    """
    lead_dict = dict(lead_data)
    lead_dict.setdefault("feedback_dapta", None)
    lead_dict.setdefault("costo_scraping", 0.0)
    lead_dict.setdefault("costo_tokens", 0.0)
    lead_dict.setdefault("costo_envio", 0.0)
    lead_dict.setdefault("campana_id", None)

    if not permitir_duplicados:
        duplicado = buscar_lead_duplicado(
            nombre_negocio = lead_dict.get("nombre_negocio", ""),
            telefono       = lead_dict.get("telefono"),
            email          = lead_dict.get("email"),
        )
        if duplicado:
            return None

    con = obtener_conexion()
    con.execute("""
        INSERT INTO leads (
            id, nombre_negocio, sector, ciudad, telefono, email, sitio_web,
            senal_dolor, tipo_senal, fuente_deteccion, canal, estado,
            costo_scraping, costo_tokens, costo_envio, fecha_deteccion, campana_id,
            feedback_dapta
        ) VALUES (
            :id, :nombre_negocio, :sector, :ciudad, :telefono, :email, :sitio_web,
            :senal_dolor, :tipo_senal, :fuente_deteccion, :canal, :estado,
            :costo_scraping, :costo_tokens, :costo_envio, :fecha_deteccion, :campana_id,
            :feedback_dapta
        )
    """, lead_dict)
    con.commit()
    con.close()
    return lead_dict["id"]


def obtener_lead_por_id(lead_id: str) -> Optional[dict]:
    """Busca un lead por su ID. Retorna None si no existe."""
    con = obtener_conexion()
    fila = con.execute(
        "SELECT * FROM leads WHERE id = ?", (lead_id,)
    ).fetchone()
    con.close()
    return dict(fila) if fila else None


def listar_leads(
    pagina: int = 1,
    tamano: int = 20,
    canal: Optional[str] = None,
    estado: Optional[str] = None,
    sector: Optional[str] = None,
) -> list[dict]:
    """Lista leads paginados con filtros opcionales."""
    condiciones = []
    params: list = []

    if canal:
        condiciones.append("canal = ?")
        params.append(canal)
    if estado:
        condiciones.append("estado = ?")
        params.append(estado)
    if sector:
        condiciones.append("sector LIKE ?")
        params.append(f"%{sector}%")

    clausula_where = ("WHERE " + " AND ".join(condiciones)) if condiciones else ""
    offset = (pagina - 1) * tamano

    con = obtener_conexion()
    filas = con.execute(
        f"""
        SELECT * FROM leads
        {clausula_where}
        ORDER BY fecha_deteccion DESC
        LIMIT ? OFFSET ?
        """,
        params + [tamano, offset]
    ).fetchall()
    con.close()
    return [dict(f) for f in filas]


def actualizar_estado_lead(lead_id: str, nuevo_estado: str, campos_extra: dict = None):
    """Cambia el estado de un lead y opcionalmente actualiza otros campos."""
    campos = {"estado": nuevo_estado}
    if campos_extra:
        campos.update(campos_extra)

    set_clausula = ", ".join(f"{k} = :{k}" for k in campos)
    campos["lead_id"] = lead_id

    con = obtener_conexion()
    con.execute(
        f"UPDATE leads SET {set_clausula} WHERE id = :lead_id",
        campos
    )
    con.commit()
    con.close()


def sumar_costo_lead(lead_id: str, campo: str, monto: float):
    """Incrementa un campo de costo (costo_scraping, costo_tokens, costo_envio)."""
    con = obtener_conexion()
    con.execute(
        f"UPDATE leads SET {campo} = {campo} + ? WHERE id = ?",
        (monto, lead_id)
    )
    con.commit()
    con.close()


def contar_leads_por_estado_y_canal() -> list[dict]:
    """
    Agrega leads por canal y estado.
    Usado para calcular métricas CPL en tiempo real.
    """
    con = obtener_conexion()
    filas = con.execute("""
        SELECT
            canal,
            estado,
            COUNT(*) as cantidad,
            SUM(costo_scraping) as total_scraping,
            SUM(costo_tokens) as total_tokens,
            SUM(costo_envio) as total_envio
        FROM leads
        GROUP BY canal, estado
    """).fetchall()
    con.close()
    return [dict(f) for f in filas]


# ---------------------------------------------------------------------------
# CRUD de EventoCosto
# ---------------------------------------------------------------------------

def registrar_evento_costo(evento: dict):
    """Inserta un evento de costo en la tabla de auditoría."""
    con = obtener_conexion()
    con.execute("""
        INSERT INTO eventos_costo (id, lead_id, tipo, monto_usd, descripcion, timestamp)
        VALUES (:id, :lead_id, :tipo, :monto_usd, :descripcion, :timestamp)
    """, evento)
    con.commit()
    con.close()


# ---------------------------------------------------------------------------
# CRUD de Campañas
# ---------------------------------------------------------------------------

def insertar_campana(campana: dict) -> str:
    """Crea una nueva campaña."""
    con = obtener_conexion()
    con.execute("""
        INSERT INTO campanas (id, nombre, sector_objetivo, canal, estado, fecha_inicio)
        VALUES (:id, :nombre, :sector_objetivo, :canal, :estado, :fecha_inicio)
    """, campana)
    con.commit()
    con.close()
    return campana["id"]


def listar_campanas() -> list[dict]:
    """Retorna todas las campañas."""
    con = obtener_conexion()
    filas = con.execute("SELECT * FROM campanas ORDER BY fecha_inicio DESC").fetchall()
    con.close()
    return [dict(f) for f in filas]
