/**
 * TablaLeads.tsx — Tabla de leads con acciones del pipeline
 * ==========================================================
 * Lista todos los leads detectados con su estado actual y botones
 * de acción para avanzar en el pipeline:
 *   Detectado → [Contactar] → Contactado → [Ver respuesta] → Respondió → [Calificar] → Calificado/Rechazado
 */

"use client";

import { useState } from "react";

// ---------------------------------------------------------------------------
// Tipos
// ---------------------------------------------------------------------------

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
  fecha_deteccion:  string;
}

interface PropsTablaLeads {
  leads:    Lead[];
  cargando?: boolean;
  onAccion: (leadId: string, accion: "contactar" | "respuesta" | "calificar") => Promise<void>;
  onAccionLote?: (accion: "contactar" | "respuesta" | "calificar") => Promise<void>;
}

// ---------------------------------------------------------------------------
// Configuración visual de estados
// ---------------------------------------------------------------------------

const CONFIG_ESTADO: Record<string, { etiqueta: string; clase: string }> = {
  detectado:  { etiqueta: "Detectado",  clase: "bg-indigo-500/10 text-indigo-400 border-indigo-500/20" },
  contactado: { etiqueta: "Contactado", clase: "bg-amber-500/10 text-amber-400 border-amber-500/20" },
  respondio:  { etiqueta: "Respondió",  clase: "bg-blue-500/10 text-blue-400 border-blue-500/20" },
  calificado: { etiqueta: "Calificado ✅", clase: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" },
  rechazado:  { etiqueta: "Rechazado",  clase: "bg-red-500/10 text-red-400 border-red-500/20" },
};

const ICONOS_CANAL: Record<string, string> = {
  email:          "📧",
  whatsapp:       "💬",
  formulario_web: "🌐",
};

// ---------------------------------------------------------------------------
// Componente principal
// ---------------------------------------------------------------------------

export default function TablaLeads({ leads, cargando, onAccion, onAccionLote }: PropsTablaLeads) {
  // IDs de leads con acción en progreso
  const [enProgreso, setEnProgreso] = useState<Set<string>>(new Set());
  const [loteEnProgreso, setLoteEnProgreso] = useState<string | null>(null);

  async function ejecutarAccion(
    leadId: string,
    accion: "contactar" | "respuesta" | "calificar"
  ) {
    setEnProgreso(prev => new Set(prev).add(leadId));
    try {
      await onAccion(leadId, accion);
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

  const cantDetectados = leads.filter(l => l.estado === "detectado").length;
  const cantContactados = leads.filter(l => l.estado === "contactado").length;
  const cantRespondieron = leads.filter(l => l.estado === "respondio").length;

  if (cargando) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-3">
        <div className="h-5 bg-slate-800 rounded w-36 cargando" />
        {[...Array(5)].map((_, i) => (
          <div key={i} className="h-14 bg-slate-800/50 rounded cargando" />
        ))}
      </div>
    );
  }

  if (!leads || leads.length === 0) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-10 text-center">
        <p className="text-4xl mb-3">🔍</p>
        <p className="text-slate-300 font-medium">No hay leads detectados aún</p>
        <p className="text-slate-500 text-sm mt-1">
          Usa el Panel de Detección para encontrar pymes con señales de dolor reales.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl shadow-xl overflow-hidden">
      {/* Encabezado */}
      <div className="px-6 py-4 border-b border-slate-800 flex flex-wrap gap-4 items-center justify-between">
        <div>
          <h2 className="text-slate-100 font-semibold text-base">Pipeline de Leads</h2>
          <p className="text-slate-400 text-xs mt-0.5">{leads.length} lead{leads.length !== 1 ? "s" : ""} en el sistema</p>
        </div>

        {/* Acciones en lote */}
        {onAccionLote && (
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-slate-500 text-xs font-medium mr-1">Procesar lote:</span>
            {cantDetectados > 0 && (
              <button
                onClick={() => ejecutarAccionLote("contactar")}
                disabled={loteEnProgreso !== null}
                className="text-xs bg-indigo-500/20 hover:bg-indigo-500/30 text-indigo-300 border border-indigo-500/30 px-3 py-1.5 rounded-lg transition-colors disabled:opacity-50 flex items-center gap-1.5"
              >
                {loteEnProgreso === "contactar" ? "⏳ Procesando..." : `📤 Contactar Todos (${cantDetectados})`}
              </button>
            )}
            {cantContactados > 0 && (
              <button
                onClick={() => ejecutarAccionLote("respuesta")}
                disabled={loteEnProgreso !== null}
                className="text-xs bg-blue-500/20 hover:bg-blue-500/30 text-blue-300 border border-blue-500/30 px-3 py-1.5 rounded-lg transition-colors disabled:opacity-50 flex items-center gap-1.5"
              >
                {loteEnProgreso === "respuesta" ? "⏳ Procesando..." : `💬 Simular Respuestas (${cantContactados})`}
              </button>
            )}
            {cantRespondieron > 0 && (
              <button
                onClick={() => ejecutarAccionLote("calificar")}
                disabled={loteEnProgreso !== null}
                className="text-xs bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/30 px-3 py-1.5 rounded-lg transition-colors disabled:opacity-50 flex items-center gap-1.5"
              >
                {loteEnProgreso === "calificar" ? "⏳ Procesando..." : `✅ Calificar Todos (${cantRespondieron})`}
              </button>
            )}
          </div>
        )}
      </div>

      {/* Tabla */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-800/60 text-slate-400 uppercase text-xs">
            <tr>
              <th className="py-3 px-4">Negocio</th>
              <th className="py-3 px-4">Canal</th>
              <th className="py-3 px-4">Señal de Dolor</th>
              <th className="py-3 px-4 text-center">Estado</th>
              <th className="py-3 px-4 text-right">Costo Total</th>
              <th className="py-3 px-4 text-center">Acción</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {leads.map((lead) => {
              const configEstado = CONFIG_ESTADO[lead.estado] || {
                etiqueta: lead.estado,
                clase: "bg-slate-500/10 text-slate-400 border-slate-500/20",
              };
              const costoTotal = (lead.costo_scraping || 0) + (lead.costo_tokens || 0) + (lead.costo_envio || 0);
              const ocupado = enProgreso.has(lead.id);

              return (
                <tr key={lead.id} className="hover:bg-slate-800/30 transition-colors">
                  {/* Negocio */}
                  <td className="py-3.5 px-4">
                    <p className="font-medium text-slate-100 truncate max-w-[160px]">
                      {lead.nombre_negocio}
                    </p>
                    <p className="text-slate-500 text-xs capitalize">
                      {lead.sector} {lead.ciudad ? `• ${lead.ciudad}` : ""}
                    </p>
                  </td>

                  {/* Canal */}
                  <td className="py-3.5 px-4">
                    <span className="text-slate-300 text-xs">
                      {ICONOS_CANAL[lead.canal] || "📡"} {lead.canal.replace("_", " ")}
                    </span>
                  </td>

                  {/* Señal de dolor */}
                  <td className="py-3.5 px-4 max-w-[220px]">
                    <p className="text-slate-400 text-xs truncate" title={lead.senal_dolor}>
                      {lead.senal_dolor.substring(0, 80)}…
                    </p>
                    <p className="text-slate-600 text-xs capitalize mt-0.5">
                      {lead.tipo_senal.replace(/_/g, " ")}
                    </p>
                  </td>

                  {/* Estado */}
                  <td className="py-3.5 px-4 text-center">
                    <span
                      className={`text-xs px-2.5 py-1 rounded-full border ${configEstado.clase}`}
                    >
                      {configEstado.etiqueta}
                    </span>
                    {lead.estado === "calificado" && lead.score_calidad_dapta > 0 && (
                      <p className="text-emerald-500 text-xs mt-0.5">
                        Score: {(lead.score_calidad_dapta * 100).toFixed(0)}%
                      </p>
                    )}
                  </td>

                  {/* Costo total */}
                  <td className="py-3.5 px-4 text-right">
                    <span className="text-amber-400 text-xs font-mono">
                      ${costoTotal.toFixed(4)}
                    </span>
                    <span className="text-slate-600 text-xs ml-1">USD</span>
                  </td>

                  {/* Botón de acción */}
                  <td className="py-3.5 px-4 text-center">
                    {lead.estado === "detectado" && (
                      <button
                        onClick={() => ejecutarAccion(lead.id, "contactar")}
                        disabled={ocupado}
                        className="text-xs bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-400 border border-indigo-500/20 px-3 py-1.5 rounded-lg transition-colors disabled:opacity-50"
                      >
                        {ocupado ? "⏳" : "📤 Contactar"}
                      </button>
                    )}
                    {lead.estado === "contactado" && (
                      <button
                        onClick={() => ejecutarAccion(lead.id, "respuesta")}
                        disabled={ocupado}
                        className="text-xs bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 border border-blue-500/20 px-3 py-1.5 rounded-lg transition-colors disabled:opacity-50"
                      >
                        {ocupado ? "⏳" : "💬 Simular Resp."}
                      </button>
                    )}
                    {lead.estado === "respondio" && (
                      <button
                        onClick={() => ejecutarAccion(lead.id, "calificar")}
                        disabled={ocupado}
                        className="text-xs bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/20 px-3 py-1.5 rounded-lg transition-colors disabled:opacity-50"
                      >
                        {ocupado ? "⏳" : "✅ Calificar"}
                      </button>
                    )}
                    {(lead.estado === "calificado" || lead.estado === "rechazado") && (
                      <span className="text-slate-600 text-xs">Finalizado</span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
