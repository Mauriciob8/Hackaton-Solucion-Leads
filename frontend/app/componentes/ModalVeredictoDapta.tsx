/**
 * ModalVeredictoDapta.tsx — Visualizador de Calificación del Agente Dapta
 * =======================================================================
 * Muestra el análisis oficial y veredicto emitido por el Agente de Texto
 * de Dapta (ID: a2f51962-1754-4ff4-a5d3-0082625607cc) para una empresa y su categoría.
 */

"use client";

import { Lead } from "./TablaLeads";

interface PropsModalVeredictoDapta {
  lead: Lead | null;
  onCerrar: () => void;
  onAbrirWidget?: (lead: Lead) => void;
  onRecalificar?: (leadId: string) => Promise<void>;
}

export default function ModalVeredictoDapta({
  lead,
  onCerrar,
  onAbrirWidget,
  onRecalificar,
}: PropsModalVeredictoDapta) {
  if (!lead) return null;

  const esCalificado = lead.estado === "calificado";
  const esNoCalificado = lead.estado === "no_calificado" || lead.estado === "rechazado";
  const esEnRevision = lead.estado === "en_revision";

  const colorBanner = esCalificado
    ? "from-emerald-600 to-teal-700 text-white"
    : esNoCalificado
    ? "from-rose-600 to-red-700 text-white"
    : "from-purple-600 to-indigo-700 text-white";

  const badgeEstado = esCalificado
    ? { label: "Calificado por Dapta ✅", bg: "bg-emerald-100 text-emerald-800 border-emerald-300" }
    : esNoCalificado
    ? { label: "No Calificado por Dapta ❌", bg: "bg-rose-100 text-rose-800 border-rose-300" }
    : { label: "En Revisión por Dapta ⚠️", bg: "bg-purple-100 text-purple-800 border-purple-300" };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs">
      <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 max-w-xl w-full overflow-hidden animate-in fade-in zoom-in duration-200">
        {/* Encabezado */}
        <div className={`p-5 bg-gradient-to-r ${colorBanner} flex items-center justify-between`}>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xl">🤖</span>
              <h3 className="font-extrabold text-lg text-white">
                Veredicto Agente Dapta
              </h3>
            </div>
            <p className="text-xs text-white/85 mt-0.5 font-mono">
              Agente: Susan • ID: a2f51962-1754-4ff4-a5d3-0082625607cc
            </p>
          </div>
          <button
            onClick={onCerrar}
            className="w-8 h-8 rounded-full bg-white/20 hover:bg-white/30 text-white flex items-center justify-center transition-colors font-bold text-sm"
          >
            ✕
          </button>
        </div>

        {/* Contenido */}
        <div className="p-6 space-y-4 max-h-[75vh] overflow-y-auto">
          {/* Ficha de la Empresa y Categoría */}
          <div className="bg-slate-50 border border-slate-200/80 rounded-xl p-4">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div>
                <p className="text-xs font-semibold uppercase text-slate-400">
                  Empresa Evaluada
                </p>
                <h4 className="text-base font-extrabold text-slate-900">
                  {lead.nombre_negocio}
                </h4>
              </div>
              <span className="inline-flex items-center gap-1.5 text-xs font-bold bg-indigo-50 text-indigo-700 border border-indigo-200 px-3 py-1 rounded-lg">
                🏷️ Categoría: {lead.sector}
              </span>
            </div>

            <div className="grid grid-cols-2 gap-2 mt-3 pt-3 border-t border-slate-200/60 text-xs">
              <div>
                <span className="text-slate-400">Canal de Contacto:</span>
                <span className="font-semibold text-slate-700 ml-1.5 capitalize">
                  {lead.canal.replace("_", " ")}
                </span>
              </div>
              <div>
                <span className="text-slate-400">Respuesta Sondeo:</span>
                <span className="font-semibold text-slate-700 ml-1.5">
                  Opción {lead.opcion_respondida || "A"}
                </span>
              </div>
            </div>
          </div>

          {/* Estado asignado y Score */}
          <div className="flex items-center justify-between p-4 bg-slate-50/70 border border-slate-200 rounded-xl">
            <div>
              <p className="text-[11px] font-semibold text-slate-400 uppercase">
                Estado Asignado en el Pipeline
              </p>
              <div className="mt-1">
                <span className={`inline-flex items-center text-xs px-3 py-1 rounded-full border font-bold ${badgeEstado.bg}`}>
                  {badgeEstado.label}
                </span>
              </div>
            </div>
            {(lead.score_calidad_dapta > 0 || lead.feedback_dapta) && (
              <div className="text-right">
                <p className="text-[11px] font-semibold text-slate-400 uppercase">
                  Score de Calidad
                </p>
                <p className="text-xl font-extrabold text-slate-900">
                  {(lead.score_calidad_dapta * 100).toFixed(0)}%
                </p>
              </div>
            )}
          </div>

          {/* Justificación y Mensaje del Agente Dapta */}
          <div>
            <div className="flex items-center gap-1.5 mb-2">
              <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                Respuesta del Agente de Texto Dapta
              </span>
              <span className="text-[10px] bg-slate-100 text-slate-500 px-1.5 py-0.5 rounded font-mono">
                widget-v2
              </span>
            </div>
            <div className="bg-slate-900 text-slate-100 p-4 rounded-xl text-xs font-sans leading-relaxed border border-slate-800 whitespace-pre-wrap shadow-inner">
              {lead.feedback_dapta ||
                "Calificación realizada con éxito por la Agente Susan de Dapta según los criterios de HackatonPrueba (necesidad, categoría, interacciones e ingresos)."}
            </div>
          </div>
        </div>

        {/* Pie del Modal */}
        <div className="p-4 bg-slate-50 border-t border-slate-200 flex flex-wrap items-center justify-between gap-2">
          {onAbrirWidget && (
            <button
              onClick={() => {
                onAbrirWidget(lead);
                onCerrar();
              }}
              className="text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 px-3.5 py-2 rounded-xl transition-colors shadow-xs flex items-center gap-1.5"
            >
              💬 Abrir Chat con Susan (Dapta)
            </button>
          )}

          <div className="flex items-center gap-2 ml-auto">
            {onRecalificar && (
              <button
                onClick={async () => {
                  await onRecalificar(lead.id);
                  onCerrar();
                }}
                className="text-xs font-semibold text-slate-700 bg-white hover:bg-slate-100 border border-slate-300 px-3 py-2 rounded-xl transition-colors"
              >
                🔄 Recalificar con Dapta
              </button>
            )}
            <button
              onClick={onCerrar}
              className="text-xs font-semibold text-slate-600 hover:text-slate-900 px-3 py-2 rounded-xl transition-colors"
            >
              Cerrar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
