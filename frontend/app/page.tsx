/**
 * page.tsx — Dashboard principal del Motor de Leads
 * ==================================================
 * Integra todos los componentes en un dashboard de 4 secciones:
 *   1. KPI Cards (TarjetaResumen)   — Métricas globales del sistema
 *   2. Panel de Detección           — Lanzar el scraper
 *   3. Funnel de Conversión         — Visualización por etapa
 *   4. Tabla CPL por Canal          — Comparativa de costos
 *   5. Pipeline de Leads            — Lista interactiva de prospectos
 *
 * Toda la lógica de llamadas a la API está centralizada aquí.
 */

"use client";

import { useEffect, useState, useCallback } from "react";

import TarjetaResumen, { DatosResumen }     from "./componentes/TarjetaResumen";
import GraficoCPL,     { MetricaCanal }     from "./componentes/GraficoCPL";
import EstadoPipeline, { DatoFunnel }       from "./componentes/EstadoPipeline";
import TablaLeads,     { Lead }             from "./componentes/TablaLeads";
import PanelSondeo                          from "./componentes/PanelSondeo";

// URL base del backend FastAPI
const API_URL = "http://127.0.0.1:8000";

// ---------------------------------------------------------------------------
// Tipos de estado global
// ---------------------------------------------------------------------------

interface EstadoApp {
  resumen:   DatosResumen | null;
  canales:   MetricaCanal[];
  funnel:    DatoFunnel[];
  leads:     Lead[];
  modoDemo:  boolean;
  error:     string | null;
}

const ESTADO_INICIAL: EstadoApp = {
  resumen:  null,
  canales:  [],
  funnel:   [],
  leads:    [],
  modoDemo: false,
  error:    null,
};

const RESUMEN_DEMO: DatosResumen = {
  total_leads_sistema:  195,
  total_calificados:    22,
  costo_total_usd:      4.29,
  cpl_promedio_global:  0.195,
  canal_mas_eficiente:  "Formulario Web",
  mejor_cpl_calificado: 0.65,
};

// ---------------------------------------------------------------------------
// Hook de carga de datos
// ---------------------------------------------------------------------------

function useDatosDashboard() {
  const [estado, setEstado] = useState<EstadoApp>(ESTADO_INICIAL);
  const [cargando, setCargando] = useState(true);

  const cargarTodos = useCallback(async () => {
    setCargando(true);
    try {
      const [resMetricas, resFunnel, resResumen, resLeads] = await Promise.all([
        fetch(`${API_URL}/api/metricas`),
        fetch(`${API_URL}/api/metricas/funnel`),
        fetch(`${API_URL}/api/metricas/resumen`),
        fetch(`${API_URL}/api/leads?tamano=50`),
      ]);

      const datMetricas = await resMetricas.json();
      const datFunnel   = await resFunnel.json();
      const datResumen  = await resResumen.json();
      const datLeads    = await resLeads.json();

      setEstado({
        canales:  datMetricas.canales  || [],
        funnel:   datFunnel.etapas     || [],
        resumen:  datResumen           || RESUMEN_DEMO,
        leads:    datLeads.leads       || [],
        modoDemo: datMetricas.modo_demo || false,
        error:    null,
      });
    } catch {
      // Si el backend no está disponible, mostrar datos demo
      const { default: datosDemoCompletos } = await import("./datos_demo.json");
      setEstado({
        canales:  datosDemoCompletos.canales,
        funnel:   datosDemoCompletos.funnel,
        resumen:  RESUMEN_DEMO,
        leads:    [],
        modoDemo: true,
        error:    "Backend no disponible — mostrando datos de demostración",
      });
    } finally {
      setCargando(false);
    }
  }, []);

  useEffect(() => {
    cargarTodos();
  }, [cargarTodos]);

  return { estado, cargando, recargar: cargarTodos };
}

// ---------------------------------------------------------------------------
// Componente principal
// ---------------------------------------------------------------------------

export default function PaginaPrincipal() {
  const { estado, cargando, recargar } = useDatosDashboard();
  const [detectando, setDetectando] = useState(false);
  const [ultimaDeteccion, setUltimaDeteccion] = useState<{
    cantidad: number; timestamp: string;
  } | null>(null);

  // -- Detectar nuevos leads --
  async function handleDetectar(
    sector: string,
    ciudad: string,
    canal:  string,
    cantidad: number
  ) {
    setDetectando(true);
    try {
      const res = await fetch(`${API_URL}/api/leads/detectar`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          sector:           sector || null,
          ciudad:           ciudad || null,
          canal_preferido:  canal,
          cantidad_maxima:  cantidad,
        }),
      });
      const data = await res.json();
      const ahora = new Date().toLocaleTimeString("es-CO", { hour: "2-digit", minute: "2-digit" });
      setUltimaDeteccion({ cantidad: data.leads_detectados || 0, timestamp: ahora });
      await recargar();
    } catch {
      setUltimaDeteccion(null);
      console.error("Error al detectar leads");
    } finally {
      setDetectando(false);
    }
  }

  // -- Ejecutar acción en un lead --
  async function handleAccionLead(
    leadId: string,
    accion: "contactar" | "respuesta" | "calificar"
  ) {
    try {
      if (accion === "contactar") {
        await fetch(`${API_URL}/api/leads/${leadId}/contactar`, { method: "POST" });
      } else if (accion === "respuesta") {
        // Simular respuesta aleatoria A o B para el demo
        const opcion = Math.random() > 0.5 ? "A" : "B";
        await fetch(`${API_URL}/api/leads/${leadId}/respuesta`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ lead_id: leadId, opcion }),
        });
      } else if (accion === "calificar") {
        await fetch(`${API_URL}/api/leads/${leadId}/calificar`, { method: "POST" });
      }
      await recargar();
    } catch {
      console.error(`Error al ejecutar acción '${accion}' en lead ${leadId}`);
    }
  }

  // -- Ejecutar acción en lote sobre todos los leads de una etapa --
  async function handleAccionLote(
    accion: "contactar" | "respuesta" | "calificar"
  ) {
    try {
      await fetch(`${API_URL}/api/leads/procesar-lote`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ accion, limite: 50 }),
      });
      await recargar();
    } catch {
      console.error(`Error al ejecutar acción en lote '${accion}'`);
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 text-white">
      {/* ------------------------------------------------------------------ */}
      {/* HEADER                                                              */}
      {/* ------------------------------------------------------------------ */}
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-indigo-400 flex items-center gap-2">
              ⚡ Motor de Leads
            </h1>
            <p className="text-slate-500 text-xs mt-0.5">
              Intent-Based Lead Engine + Unit Economics Tracker
            </p>
          </div>
          <div className="flex items-center gap-3">
            {estado.modoDemo && (
              <span className="text-xs bg-amber-500/10 text-amber-400 border border-amber-500/20 px-3 py-1 rounded-full">
                📊 Modo Demo
              </span>
            )}
            <button
              onClick={recargar}
              disabled={cargando}
              className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 px-3 py-1.5 rounded-lg transition-colors disabled:opacity-50"
            >
              {cargando ? "⏳" : "🔄"} Actualizar
            </button>
          </div>
        </div>
      </header>

      {/* ------------------------------------------------------------------ */}
      {/* BANNER DE ERROR (si backend no disponible)                          */}
      {/* ------------------------------------------------------------------ */}
      {estado.error && (
        <div className="max-w-7xl mx-auto px-6 pt-4">
          <div className="bg-red-950/50 border border-red-500/30 rounded-lg px-4 py-3 text-red-300 text-sm flex items-start gap-2">
            <span className="text-red-400 mt-0.5">⚠️</span>
            <div>
              <p className="font-medium">{estado.error}</p>
              <p className="text-red-400 text-xs mt-0.5">
                Asegúrate de ejecutar:{" "}
                <code className="bg-red-900/40 px-1.5 py-0.5 rounded font-mono">
                  uvicorn backend.main:app --reload --port 8000
                </code>
              </p>
            </div>
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------------ */}
      {/* CONTENIDO PRINCIPAL                                                 */}
      {/* ------------------------------------------------------------------ */}
      <div className="max-w-7xl mx-auto px-6 py-6 space-y-6">

        {/* 1. KPI Cards */}
        <TarjetaResumen
          datos={estado.resumen || RESUMEN_DEMO}
          cargando={cargando && !estado.resumen}
        />

        {/* 2. Panel de Detección de Leads */}
        <PanelSondeo
          onDetectar={handleDetectar}
          detectando={detectando}
          ultimaDeteccion={ultimaDeteccion}
        />

        {/* 3. Funnel + CPL en grid de 2 columnas */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <EstadoPipeline
            etapas={estado.funnel}
            modoDemo={estado.modoDemo}
            cargando={cargando && estado.funnel.length === 0}
          />
          <GraficoCPL
            canales={estado.canales}
            modoDemo={estado.modoDemo}
            cargando={cargando && estado.canales.length === 0}
          />
        </div>

        {/* 4. Pipeline de Leads */}
        <TablaLeads
          leads={estado.leads}
          cargando={cargando && estado.leads.length === 0}
          onAccion={handleAccionLead}
          onAccionLote={handleAccionLote}
        />

        {/* Footer */}
        <footer className="text-center text-slate-700 text-xs pb-4 border-t border-slate-800 pt-4">
          Motor de Leads — Hackathon Dapta 2024 · Intent-Based Lead Engine + Unit Economics Tracker
        </footer>
      </div>
    </main>
  );
}