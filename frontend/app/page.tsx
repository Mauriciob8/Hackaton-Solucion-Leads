/**
 * page.tsx — Dashboard Admin Principal (Motor de Leads)
 * =======================================================
 * Arquitectura modular completa:
 * - Sidebar lateral (Navegación entre módulos)
 * - Navbar superior (Buscador, Entorno, Exportar CSV, Perfil)
 * - Vistas centralizadas dinámicas:
 *     1. Dashboard General (KPIs, Smart Router, Embudo y CPL)
 *     2. Detección Activa (Scraper)
 *     3. Pipeline de Prospectos (Tabla Interactiva)
 *     4. Unit Economics & CPL (Análisis Financiero)
 *     5. Base RAG (Catálogo Dapta)
 */

"use client";

import { useEffect, useState, useCallback } from "react";

import Sidebar, { ModuloActivo }             from "./componentes/Sidebar";
import Navbar                               from "./componentes/Navbar";
import TarjetaResumen, { DatosResumen }     from "./componentes/TarjetaResumen";
import GraficoCPL,     { MetricaCanal }     from "./componentes/GraficoCPL";
import EstadoPipeline, { DatoFunnel }       from "./componentes/EstadoPipeline";
import TablaLeads,     { Lead }             from "./componentes/TablaLeads";
import PanelSondeo                          from "./componentes/PanelSondeo";
import TarjetaSmartRouter, { DatosSmartRouter } from "./componentes/TarjetaSmartRouter";
import VistaCatalogoRAG                     from "./componentes/VistaCatalogoRAG";
import ModalAuditoriaRAG                    from "./componentes/ModalAuditoriaRAG";
import ModalConversacion                    from "./componentes/ModalConversacion";

const API_URL = (() => {
  const configuredUrl = process.env.NEXT_PUBLIC_API_URL?.trim();
  if (!configuredUrl) return "http://127.0.0.1:8000";
  return `${configuredUrl.includes("://") ? "" : "https://"}${configuredUrl}`.replace(/\/+$/, "");
})();

interface EstadoApp {
  resumen:     DatosResumen | null;
  canales:     MetricaCanal[];
  funnel:      DatoFunnel[];
  leads:       Lead[];
  smartRouter: DatosSmartRouter | null;
  modoDemo:    boolean;
  error:       string | null;
}

const ESTADO_INICIAL: EstadoApp = {
  resumen:     null,
  canales:     [],
  funnel:      [],
  leads:       [],
  smartRouter: null,
  modoDemo:    false,
  error:       null,
};

const RESUMEN_DEMO: DatosResumen = {
  total_leads_sistema:  195,
  total_calificados:    22,
  costo_total_usd:      4.29,
  cpl_promedio_global:  0.195,
  canal_mas_eficiente:  "Formulario Web",
  mejor_cpl_calificado: 0.65,
};

function useDatosDashboard() {
  const [estado, setEstado] = useState<EstadoApp>(ESTADO_INICIAL);
  const [cargando, setCargando] = useState(true);

  const cargarTodos = useCallback(async () => {
    setCargando(true);
    try {
      const [resMetricas, resFunnel, resResumen, resLeads, resSmartRouter] = await Promise.all([
        fetch(`${API_URL}/api/metricas`),
        fetch(`${API_URL}/api/metricas/funnel`),
        fetch(`${API_URL}/api/metricas/resumen`),
        fetch(`${API_URL}/api/leads?tamano=100`),
        fetch(`${API_URL}/api/metricas/smart-router`),
      ]);

      const datMetricas    = await resMetricas.json();
      const datFunnel      = await resFunnel.json();
      const datResumen     = await resResumen.json();
      const datLeads       = await resLeads.json();
      const datSmartRouter = await resSmartRouter.json();

      setEstado({
        canales:     datMetricas.canales   || [],
        funnel:      datFunnel.etapas      || [],
        resumen:     datResumen            || RESUMEN_DEMO,
        leads:       datLeads.leads        || [],
        smartRouter: datSmartRouter        || null,
        modoDemo:    datMetricas.modo_demo || false,
        error:       null,
      });
    } catch {
      const { default: datosDemoCompletos } = await import("./datos_demo.json");
      setEstado({
        canales:     datosDemoCompletos.canales,
        funnel:      datosDemoCompletos.funnel,
        resumen:     RESUMEN_DEMO,
        leads:       [],
        smartRouter: {
          hay_recomendacion: true,
          canal_recomendado: "WhatsApp Cloud API",
          canal_recomendado_id: "whatsapp",
          cpl_recomendado: 0.85,
          canal_alternativo: "Email Transaccional",
          cpl_alternativo: 1.10,
          ahorro_porcentual: 22.7,
          total_canales_comparados: 3,
          mensaje: "Recomendación: Reasigne el presupuesto a WhatsApp Cloud API. Genera un CPL Calificado 22% menor que el Email.",
          modo_demo: true
        },
        modoDemo:    true,
        error:       "Backend no disponible — mostrando datos de demostración",
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

export default function PaginaPrincipal() {
  const { estado, cargando, recargar } = useDatosDashboard();

  // Módulo activo en el Sidebar
  const [moduloActivo, setModuloActivo] = useState<ModuloActivo>("dashboard");

  // Búsqueda global en el Navbar
  const [busqueda, setBusqueda] = useState("");

  // Estado del scraper
  const [detectando, setDetectando] = useState(false);
  const [ultimaDeteccion, setUltimaDeteccion] = useState<{
    cantidad: number; timestamp: string;
  } | null>(null);

  // Modales y Notificaciones
  const [modalAuditoria, setModalAuditoria] = useState<Lead | null>(null);
  const [modalConversacion, setModalConversacion] = useState<Lead | null>(null);
  const [notificacionDapta, setNotificacionDapta] = useState<{
    empresa: string;
    categoria: string;
    estado: string;
    score: number;
    feedback: string;
  } | null>(null);
  const [errorAccion, setErrorAccion] = useState<string | null>(null);

  function handleDescargarCSV() {
    window.open(`${API_URL}/api/leads/calificados/exportar-csv`, "_blank");
  }

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
      // Si estamos en detección, cambiar al pipeline para ver los resultados
      setModuloActivo("pipeline");
    } catch {
      setUltimaDeteccion(null);
      console.error("Error al detectar leads");
    } finally {
      setDetectando(false);
    }
  }

  async function handleAccionLead(
    leadId: string,
    accion: "contactar" | "respuesta" | "calificar"
  ): Promise<boolean> {
    setErrorAccion(null);
    try {
      let res: Response;
      if (accion === "contactar") {
        res = await fetch(`${API_URL}/api/leads/${leadId}/contactar`, { method: "POST" });
      } else if (accion === "respuesta") {
        const opcion = Math.random() > 0.5 ? "A" : "B";
        res = await fetch(`${API_URL}/api/leads/${leadId}/respuesta`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ lead_id: leadId, opcion }),
        });
      } else {
        res = await fetch(`${API_URL}/api/leads/${leadId}/calificar`, { method: "POST" });
      }
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || `No se pudo ejecutar la acción '${accion}'.`);
      }
      if (accion === "calificar") {
        if (data && data.nuevo_estado) {
          setNotificacionDapta({
            empresa: data.nombre_negocio || "Empresa",
            categoria: data.categoria || "Categoría",
            estado: data.nuevo_estado,
            score: data.score_calidad_porcentaje,
            feedback: data.feedback_dapta || data.mensaje,
          });
        }
      }
      await recargar();
      return true;
    } catch (error) {
      const mensaje = error instanceof Error ? error.message : "Error inesperado al ejecutar la acción.";
      setErrorAccion(mensaje);
      console.error(`Error al ejecutar acción '${accion}' en lead ${leadId}:`, error);
      return false;
    }
  }

  async function handleAccionLote(
    accion: "contactar" | "respuesta" | "calificar"
  ) {
    setErrorAccion(null);
    try {
      const res = await fetch(`${API_URL}/api/leads/procesar-lote`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ accion, limite: 50 }),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || `No se pudo ejecutar la acción en lote '${accion}'.`);
      }
      if (data.errores > 0) {
        setErrorAccion(`${data.errores} lead(s) no pudieron procesarse. Revisa la conexión con Dapta.`);
      }
      await recargar();
    } catch (error) {
      const mensaje = error instanceof Error ? error.message : "Error inesperado al procesar el lote.";
      setErrorAccion(mensaje);
      console.error(`Error al ejecutar acción en lote '${accion}':`, error);
    }
  }

  return (
    <div className="min-h-screen flex bg-[#f8f9fc] text-slate-800">
      {/* 1. Sidebar Lateral */}
      <Sidebar
        moduloActivo={moduloActivo}
        onCambiarModulo={setModuloActivo}
        totalLeads={estado.leads.length || (estado.resumen?.total_leads_sistema ?? 0)}
        totalCalificados={estado.resumen?.total_calificados ?? 0}
      />

      {/* 2. Área Principal de Contenido */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Navbar Superior */}
        <Navbar
          busqueda={busqueda}
          onCambiarBusqueda={setBusqueda}
          modoDemo={estado.modoDemo}
          cargando={cargando}
          onRecargar={recargar}
          onExportarCSV={handleDescargarCSV}
        />

        {/* Banner de aviso si el backend está desconectado */}
        {estado.error && (
          <div className="px-8 pt-4">
            <div className="bg-amber-50 border border-amber-200 rounded-xl px-4 py-3 text-amber-800 text-xs flex items-center justify-between">
              <span className="flex items-center gap-2 font-medium">
                <span>⚠️</span> {estado.error}
              </span>
              <code className="bg-white border border-amber-200 px-2 py-0.5 rounded font-mono text-[11px]">
                uvicorn backend.main:app --reload
              </code>
            </div>
          </div>
        )}
        {errorAccion && (
          <div className="px-8 pt-4" role="alert">
            <div className="bg-rose-50 border border-rose-200 rounded-xl px-4 py-3 text-rose-800 text-xs flex items-center justify-between">
              <span className="flex items-center gap-2 font-medium">
                <span>⚠️</span> {errorAccion}
              </span>
              <button
                onClick={() => setErrorAccion(null)}
                className="text-rose-700 hover:text-rose-900 font-bold"
                aria-label="Cerrar mensaje de error"
              >
                ✕
              </button>
            </div>
          </div>
        )}

        {/* Contenedor de Vistas */}
        <main className="p-8 space-y-6 flex-1 max-w-[1600px] w-full">
          {/* VISTA 1: DASHBOARD GENERAL */}
          {moduloActivo === "dashboard" && (
            <div className="space-y-6 animate-in fade-in duration-200">
              {/* Tarjetas KPI */}
              <TarjetaResumen
                datos={estado.resumen || RESUMEN_DEMO}
                cargando={cargando && !estado.resumen}
              />

              {/* Recomendador Predictivo Smart Router */}
              <TarjetaSmartRouter
                datos={estado.smartRouter}
                cargando={cargando && !estado.smartRouter}
              />

              {/* Grid 2 Columnas: Embudo + Comparativa de CPL */}
              <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
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

              {/* Vista previa rápida del Pipeline */}
              <div>
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-slate-800 font-bold text-sm">
                    Prospectos Recientes en Pipeline
                  </h3>
                  <button
                    onClick={() => setModuloActivo("pipeline")}
                    className="text-xs font-semibold text-indigo-600 hover:text-indigo-800"
                  >
                    Ver Pipeline Completo ({estado.leads.length}) →
                  </button>
                </div>
                <TablaLeads
                  leads={estado.leads.slice(0, 10)}
                  cargando={cargando && estado.leads.length === 0}
                  onAccion={handleAccionLead}
                  onAccionLote={handleAccionLote}
                  onVerAuditoria={(lead) => setModalAuditoria(lead)}
                  onVerConversacion={(lead) => setModalConversacion(lead)}
                  filtroExterno={busqueda}
                />
              </div>
            </div>
          )}

          {/* VISTA 2: DETECCIÓN ACTIVA (SCRAPING) */}
          {moduloActivo === "deteccion" && (
            <div className="space-y-6 animate-in fade-in duration-200">
              <PanelSondeo
                onDetectar={handleDetectar}
                detectando={detectando}
                ultimaDeteccion={ultimaDeteccion}
              />
            </div>
          )}

          {/* VISTA 3: PIPELINE DE PROSPECTOS */}
          {moduloActivo === "pipeline" && (
            <div className="space-y-6 animate-in fade-in duration-200">
              <TablaLeads
                leads={estado.leads}
                cargando={cargando && estado.leads.length === 0}
                onAccion={handleAccionLead}
                onAccionLote={handleAccionLote}
                onVerAuditoria={(lead) => setModalAuditoria(lead)}
                onVerConversacion={(lead) => setModalConversacion(lead)}
                filtroExterno={busqueda}
              />
            </div>
          )}

          {/* VISTA 4: UNIT ECONOMICS & CPL */}
          {moduloActivo === "unit_economics" && (
            <div className="space-y-6 animate-in fade-in duration-200">
              <TarjetaSmartRouter
                datos={estado.smartRouter}
                cargando={cargando && !estado.smartRouter}
              />
              <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                <GraficoCPL
                  canales={estado.canales}
                  modoDemo={estado.modoDemo}
                  cargando={cargando && estado.canales.length === 0}
                />
                <EstadoPipeline
                  etapas={estado.funnel}
                  modoDemo={estado.modoDemo}
                  cargando={cargando && estado.funnel.length === 0}
                />
              </div>
            </div>
          )}

          {/* VISTA 5: BASE DE CONOCIMIENTO RAG (CATÁLOGO DAPTA) */}
          {moduloActivo === "catalogo_rag" && (
            <div className="space-y-6 animate-in fade-in duration-200">
              <VistaCatalogoRAG />
            </div>
          )}
        </main>

        {/* Footer Admin */}
        <footer className="px-8 py-4 border-t border-slate-200/80 bg-white text-slate-400 text-xs flex flex-col sm:flex-row items-center justify-between gap-2 mt-auto">
          <span>
            © 2026 Motor de Leads — Hackathon Dapta · Intent-Based Lead Engine + Unit Economics Tracker
          </span>
        </footer>
      </div>

      {/* Modales */}
      {modalAuditoria && (
        <ModalAuditoriaRAG
          leadId={modalAuditoria.id}
          apiUrl={API_URL}
          onCerrar={() => setModalAuditoria(null)}
        />
      )}

      {modalConversacion && (
        <ModalConversacion
          lead={modalConversacion}
          onCerrar={() => setModalConversacion(null)}
        />
      )}

      {/* Notificación Flotante de Calificación Dapta */}
      {notificacionDapta && (
        <div className="fixed bottom-6 right-20 z-40 max-w-md bg-white border border-slate-300 rounded-2xl shadow-xl p-4 animate-in slide-in-from-bottom-5 duration-300 flex items-start gap-3">
          <span className="text-2xl mt-0.5">🤖</span>
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between gap-2">
              <h4 className="text-xs font-bold text-slate-900 truncate">
                Agente Dapta calificó a: {notificacionDapta.empresa}
              </h4>
              <button
                onClick={() => setNotificacionDapta(null)}
                className="text-slate-400 hover:text-slate-600 text-xs font-bold"
              >
                ✕
              </button>
            </div>
            <p className="text-[11px] text-slate-500 mt-0.5">
              Categoría: <strong className="text-indigo-600">{notificacionDapta.categoria}</strong> • Nuevo Estado:{" "}
              <strong className="text-emerald-700 capitalize">{notificacionDapta.estado.replace("_", " ")}</strong> • Score:{" "}
              <strong className="text-slate-800">{notificacionDapta.score.toFixed(0)}%</strong>
            </p>
            <p className="text-xs text-slate-700 mt-2 bg-slate-50 p-2.5 rounded-lg border border-slate-200/80 line-clamp-3">
              &quot;{notificacionDapta.feedback}&quot;
            </p>
          </div>
        </div>
      )}
    </div>
  );
}