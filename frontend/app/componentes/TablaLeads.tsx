/**
 * TablaLeads.tsx — Pipeline interactivo de prospectos (Estilo SaaS Empresarial)
 * ============================================================================
 * Tabla corporativa con búsqueda local, filtros por canal y estado,
 * badges claros, costos atómicos y botones rápidos de acción (RAG, Chat, Pipeline).
 */

"use client";

import { useState, useMemo } from "react";
import ModalVeredictoDapta from "./ModalVeredictoDapta";

declare global {
  interface Window {
    setConversationParams?: (params: Record<string, unknown>) => void;
    toggleDaptaWidgetChat?: () => void;
    daptaAgent?: unknown;
  }
}

export interface Lead {
  id:               string;
  nombre_negocio:   string;
  sector:           string;
  ciudad:           string | null;
  canal:            string;
  estado:           string;
  senal_dolor:      string;
  tipo_senal:       string;
  costo_scraping:   number;
  costo_tokens:     number;
  costo_envio:      number;
  opcion_respondida: string | null;
  calificado_dapta:  number;
  score_calidad_dapta: number;
  feedback_dapta?:    string | null;
  fecha_deteccion:  string;
  pregunta_sondeo?:    string | null;
  propuesta_generada?: string | null;
}

interface PropsTablaLeads {
  leads:    Lead[];
  cargando?: boolean;
  onAccion: (leadId: string, accion: "contactar" | "respuesta" | "calificar") => Promise<void | boolean>;
  onAccionLote?: (accion: "contactar" | "respuesta" | "calificar") => Promise<void>;
  onVerAuditoria?: (lead: Lead) => void;
  onVerConversacion?: (lead: Lead) => void;
  filtroExterno?: string;
}

const CONFIG_ESTADO: Record<string, { etiqueta: string; clase: string; dot: string }> = {
  detectado:     { etiqueta: "Detectado",        clase: "bg-indigo-50 text-indigo-700 border-indigo-200", dot: "bg-indigo-500" },
  contactado:    { etiqueta: "Contactado",       clase: "bg-amber-50 text-amber-700 border-amber-200", dot: "bg-amber-500" },
  respondio:     { etiqueta: "Respondió",        clase: "bg-blue-50 text-blue-700 border-blue-200", dot: "bg-blue-500" },
  calificado:    { etiqueta: "Calificado ✅",    clase: "bg-emerald-50 text-emerald-800 border-emerald-300 font-bold shadow-2xs", dot: "bg-emerald-500" },
  no_calificado: { etiqueta: "No calificado ❌",  clase: "bg-rose-50 text-rose-700 border-rose-200 font-semibold", dot: "bg-rose-500" },
  en_revision:   { etiqueta: "En revisión ⚠️",   clase: "bg-purple-50 text-purple-700 border-purple-200 font-semibold", dot: "bg-purple-500" },
  rechazado:     { etiqueta: "Rechazado ❌",     clase: "bg-slate-100 text-slate-600 border-slate-200 font-medium", dot: "bg-slate-400" },
};

const ICONOS_CANAL: Record<string, string> = {
  email:          "📧",
  whatsapp:       "💬",
  formulario_web: "🌐",
};

export default function TablaLeads({
  leads,
  cargando,
  onAccion,
  onAccionLote,
  onVerAuditoria,
  onVerConversacion,
  filtroExterno = "",
}: PropsTablaLeads) {
  const [enProgreso, setEnProgreso] = useState<Set<string>>(new Set());
  const [loteEnProgreso, setLoteEnProgreso] = useState<string | null>(null);
  const [leadVeredicto, setLeadVeredicto] = useState<Lead | null>(null);

  // Filtros locales
  const [filtroCanal, setFiltroCanal] = useState<string>("");
  const [filtroEstado, setFiltroEstado] = useState<string>("");

  function abrirWidgetDapta(lead: Lead) {
    if (typeof window !== "undefined") {
      if (window.setConversationParams) {
        window.setConversationParams({
          lead_id: lead.id,
          empresa: lead.nombre_negocio,
          categoria: lead.sector,
          perfil_cliente: lead.sector,
          canal: lead.canal,
          senal_dolor: lead.senal_dolor,
        });
      }
      if (window.toggleDaptaWidgetChat) {
        window.toggleDaptaWidgetChat();
      }
    }
  }

  async function ejecutarAccion(leadId: string, accion: "contactar" | "respuesta" | "calificar") {
    setEnProgreso(prev => new Set(prev).add(leadId));
    try {
      return (await onAccion(leadId, accion)) !== false;
    } finally {
      setEnProgreso(prev => {
        const siguiente = new Set(prev);
        siguiente.delete(leadId);
        return siguiente;
      });
    }
  }

  async function ejecutarAccionLote(accion: "contactar" | "respuesta" | "calificar") {
    if (!onAccionLote) return;
    setLoteEnProgreso(accion);
    try {
      await onAccionLote(accion);
    } finally {
      setLoteEnProgreso(null);
    }
  }

  // Filtrado de leads
  const leadsFiltrados = useMemo(() => {
    return leads.filter((lead) => {
      const coincideBusqueda =
        !filtroExterno ||
        lead.nombre_negocio.toLowerCase().includes(filtroExterno.toLowerCase()) ||
        lead.sector.toLowerCase().includes(filtroExterno.toLowerCase()) ||
        (lead.ciudad && lead.ciudad.toLowerCase().includes(filtroExterno.toLowerCase())) ||
        lead.senal_dolor.toLowerCase().includes(filtroExterno.toLowerCase());

      const coincideCanal = !filtroCanal || lead.canal === filtroCanal;
      const coincideEstado = !filtroEstado || lead.estado === filtroEstado;

      return coincideBusqueda && coincideCanal && coincideEstado;
    });
  }, [leads, filtroExterno, filtroCanal, filtroEstado]);

  const cantDetectados = leads.filter(l => l.estado === "detectado").length;
  const cantContactados = leads.filter(l => l.estado === "contactado").length;
  const cantRespondieron = leads.filter(l => l.estado === "respondio").length;

  if (cargando) {
    return (
      <div className="bg-white border border-slate-200/90 rounded-2xl p-6 shadow-xs space-y-3">
        <div className="h-6 bg-slate-100 rounded w-48 cargando" />
        {[...Array(6)].map((_, i) => (
          <div key={i} className="h-14 bg-slate-50 rounded-xl cargando" />
        ))}
      </div>
    );
  }

  if (!leads || leads.length === 0) {
    return (
      <div className="bg-white border border-slate-200/90 rounded-2xl p-12 text-center shadow-xs">
        <p className="text-4xl mb-3">🔍</p>
        <p className="text-slate-800 font-bold text-sm">No hay prospectos en el sistema</p>
        <p className="text-slate-500 text-xs mt-1">
          Utiliza el módulo de Detección Activa para extraer negocios con señales de dolor.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white border border-slate-200/90 rounded-2xl shadow-xs overflow-hidden">
      {/* Barra de control superior */}
      <div className="px-6 py-4 border-b border-slate-100 flex flex-wrap gap-4 items-center justify-between bg-slate-50/50">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-slate-900 font-bold text-base">Pipeline de Prospectos</h2>
            <span className="text-xs font-semibold bg-white text-slate-700 border border-slate-200 px-2 py-0.5 rounded-full shadow-2xs">
              {leadsFiltrados.length} de {leads.length}
            </span>
          </div>
          <p className="text-slate-500 text-xs mt-0.5">Gestión y avance del ciclo de conversión</p>
        </div>

        {/* Filtros locales */}
        <div className="flex items-center gap-2 flex-wrap">
          {/* Filtro Canal */}
          <select
            value={filtroCanal}
            onChange={(e) => setFiltroCanal(e.target.value)}
            className="text-xs bg-white border border-slate-200 text-slate-700 rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-indigo-500"
          >
            <option value="">Todos los canales</option>
            <option value="whatsapp">💬 WhatsApp</option>
            <option value="email">📧 Email</option>
            <option value="formulario_web">🌐 Formulario</option>
          </select>

          {/* Filtro Estado */}
          <select
            value={filtroEstado}
            onChange={(e) => setFiltroEstado(e.target.value)}
            className="text-xs bg-white border border-slate-200 text-slate-700 rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-indigo-500"
          >
            <option value="">Todos los estados</option>
            <option value="detectado">Detectados</option>
            <option value="contactado">Contactados</option>
            <option value="respondio">Respondieron</option>
            <option value="calificado">Calificados</option>
          </select>

          {/* Acciones en lote */}
          {onAccionLote && (
            <div className="flex items-center gap-1.5 pl-2 border-l border-slate-200">
              {cantDetectados > 0 && (
                <button
                  onClick={() => ejecutarAccionLote("contactar")}
                  disabled={loteEnProgreso !== null}
                  className="text-xs font-semibold bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200 px-2.5 py-1.5 rounded-lg transition-colors disabled:opacity-50"
                >
                  {loteEnProgreso === "contactar" ? "⏳..." : `📤 Contactar (${cantDetectados})`}
                </button>
              )}
              {cantContactados > 0 && (
                <button
                  onClick={() => ejecutarAccionLote("respuesta")}
                  disabled={loteEnProgreso !== null}
                  className="text-xs font-semibold bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 px-2.5 py-1.5 rounded-lg transition-colors disabled:opacity-50"
                >
                  {loteEnProgreso === "respuesta" ? "⏳..." : `💬 Simular Resp. (${cantContactados})`}
                </button>
              )}
              {cantRespondieron > 0 && (
                <button
                  onClick={() => ejecutarAccionLote("calificar")}
                  disabled={loteEnProgreso !== null}
                  className="text-xs font-semibold bg-emerald-50 hover:bg-emerald-100 text-emerald-800 border border-emerald-200 px-2.5 py-1.5 rounded-lg transition-colors disabled:opacity-50"
                >
                  {loteEnProgreso === "calificar" ? "⏳..." : `🤖 Calificar con Dapta (${cantRespondieron})`}
                </button>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Tabla SaaS */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="bg-slate-50/70 border-b border-slate-200 text-slate-400 uppercase tracking-wider font-semibold text-[10px]">
              <th className="py-3 px-4">Empresa & Categoría</th>
              <th className="py-3 px-3">Canal</th>
              <th className="py-3 px-4">Señal de Dolor (Pública)</th>
              <th className="py-3 px-3 text-center">Estado</th>
              <th className="py-3 px-3 text-right">Inversión</th>
              <th className="py-3 px-3 text-center">Inspección RAG</th>
              <th className="py-3 px-4 text-center">Acción</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {leadsFiltrados.map((lead) => {
              const configEstado = CONFIG_ESTADO[lead.estado] || {
                etiqueta: lead.estado,
                clase: "bg-slate-100 text-slate-700 border-slate-200",
                dot: "bg-slate-400",
              };
              const costoTotal = (lead.costo_scraping || 0) + (lead.costo_tokens || 0) + (lead.costo_envio || 0);
              const ocupado = enProgreso.has(lead.id);

              return (
                <tr key={lead.id} className="hover:bg-slate-50/80 transition-colors">
                  {/* Empresa & Categoría */}
                  <td className="py-3.5 px-4">
                    <p className="font-bold text-slate-900 truncate max-w-[170px]">
                      {lead.nombre_negocio}
                    </p>
                    <div className="flex flex-wrap items-center gap-1 mt-1">
                      <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-indigo-900 bg-indigo-50 border border-indigo-200/80 px-2 py-0.5 rounded-md">
                        🏷️ {lead.sector}
                      </span>
                      {lead.ciudad && (
                        <span className="text-slate-400 text-[10px]">
                          • {lead.ciudad}
                        </span>
                      )}
                    </div>
                  </td>

                  {/* Canal */}
                  <td className="py-3.5 px-3">
                    <span className="inline-flex items-center gap-1.5 text-slate-700 font-medium text-xs bg-slate-50 border border-slate-200/80 px-2 py-1 rounded-lg">
                      <span>{ICONOS_CANAL[lead.canal] || "📡"}</span>
                      <span className="capitalize">{lead.canal.replace("_", " ")}</span>
                    </span>
                  </td>

                  {/* Señal de dolor */}
                  <td className="py-3.5 px-4 max-w-[260px]">
                    <p className="text-slate-600 text-xs line-clamp-2 leading-relaxed" title={lead.senal_dolor}>
                      {lead.senal_dolor}
                    </p>
                    <span className="inline-block mt-1 text-[10px] font-medium text-slate-400 bg-slate-100 px-1.5 py-0.2 rounded capitalize">
                      {lead.tipo_senal.replace(/_/g, " ")}
                    </span>
                  </td>

                  {/* Estado */}
                  <td className="py-3.5 px-3 text-center">
                    <span
                      className={`inline-flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full border ${configEstado.clase}`}
                    >
                      <span className={`w-1.5 h-1.5 rounded-full ${configEstado.dot}`} />
                      {configEstado.etiqueta}
                    </span>
                    {(lead.score_calidad_dapta > 0 || lead.feedback_dapta) && (
                      <p className="text-slate-500 font-semibold text-[10px] mt-0.5">
                        Score: {(lead.score_calidad_dapta * 100).toFixed(0)}%
                      </p>
                    )}
                  </td>

                  {/* Inversión total */}
                  <td className="py-3.5 px-3 text-right">
                    <span className="text-slate-800 text-xs font-mono font-bold">
                      ${costoTotal.toFixed(4)}
                    </span>
                    <span className="text-slate-400 text-[10px] ml-1">USD</span>
                  </td>

                  {/* Inspección RAG & Chat */}
                  <td className="py-3.5 px-3 text-center">
                    <div className="flex items-center justify-center gap-1.5">
                      <button
                        onClick={() => onVerAuditoria?.(lead)}
                        title="Ver trazabilidad RAG completa"
                        className="text-xs font-semibold bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200 px-2.5 py-1 rounded-lg transition-colors shadow-2xs"
                      >
                        🔍 RAG
                      </button>
                      {(lead.estado === "respondio" || lead.estado === "calificado") && (
                        <button
                          onClick={() => onVerConversacion?.(lead)}
                          title="Ver chat interactivo WhatsApp"
                          className="text-xs font-semibold bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-200 px-2.5 py-1 rounded-lg transition-colors shadow-2xs"
                        >
                          💬 Chat
                        </button>
                      )}
                    </div>
                  </td>

                  {/* Botón de acción contextual */}
                  <td className="py-3.5 px-4 text-center">
                    {lead.estado === "detectado" && (
                      <button
                        onClick={() => ejecutarAccion(lead.id, "contactar")}
                        disabled={ocupado}
                        className="text-xs font-semibold bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-1.5 rounded-lg transition-colors shadow-xs disabled:opacity-50"
                      >
                        {ocupado ? "⏳" : "📤 Contactar"}
                      </button>
                    )}
                    {lead.estado === "contactado" && (
                      <button
                        onClick={() => ejecutarAccion(lead.id, "respuesta")}
                        disabled={ocupado}
                        className="text-xs font-semibold bg-blue-600 hover:bg-blue-700 text-white px-3 py-1.5 rounded-lg transition-colors shadow-xs disabled:opacity-50"
                      >
                        {ocupado ? "⏳" : "💬 Simular Resp."}
                      </button>
                    )}
                    {lead.estado === "respondio" && (
                      <div className="flex flex-col items-center gap-1">
                        <button
                          onClick={() => ejecutarAccion(lead.id, "calificar")}
                          disabled={ocupado}
                          title="Enviar lead y categoría a agente Dapta"
                          className="text-xs font-bold bg-emerald-600 hover:bg-emerald-700 text-white px-3 py-1.5 rounded-lg transition-colors shadow-xs disabled:opacity-50 flex items-center gap-1"
                        >
                          {ocupado ? "⏳ Evaluando..." : "🤖 Calificar (Dapta)"}
                        </button>
                        <button
                          onClick={() => abrirWidgetDapta(lead)}
                          title="Abrir chat interactivo con la Agente Susan"
                          className="text-[10px] font-semibold text-indigo-600 hover:text-indigo-800 underline"
                        >
                          💬 Chat con Susan
                        </button>
                      </div>
                    )}
                    {(lead.estado === "calificado" || lead.estado === "no_calificado" || lead.estado === "en_revision" || lead.estado === "rechazado") && (
                      <div className="flex flex-col items-center gap-1">
                        <button
                          onClick={() => setLeadVeredicto(lead)}
                          title="Ver veredicto y justificación del Agente Dapta"
                          className="text-xs font-semibold bg-slate-50 hover:bg-slate-100 text-slate-700 border border-slate-200 px-2.5 py-1 rounded-lg transition-colors shadow-2xs"
                        >
                          📋 Veredicto Dapta
                        </button>
                        <button
                          onClick={() => abrirWidgetDapta(lead)}
                          title="Chatear con Susan sobre este lead"
                          className="text-[10px] text-slate-400 hover:text-indigo-600 transition-colors"
                        >
                          💬 Chat Susan
                        </button>
                      </div>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Modal de Veredicto del Agente Dapta */}
      {leadVeredicto && (
        <ModalVeredictoDapta
          lead={leadVeredicto}
          onCerrar={() => setLeadVeredicto(null)}
          onAbrirWidget={abrirWidgetDapta}
          onRecalificar={async (id) => {
            const exito = await ejecutarAccion(id, "calificar");
            if (!exito) return false;
            const updated = leads.find((l) => l.id === id);
            if (updated) setLeadVeredicto(updated);
            return true;
          }}
        />
      )}
    </div>
  );
}
