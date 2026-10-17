/**
 * ModalConversacion.tsx — Simulador de conversación estilo WhatsApp (Diseño Moderno)
 * =================================================================================
 * Vista tipo smartphone con burbujas de WhatsApp:
 * 1. Micro-sondeo del sistema (A o B)
 * 2. Respuesta del prospecto
 * 3. Propuesta personalizada generada
 */

"use client";

import { useEffect } from "react";
import type { Lead } from "./TablaLeads";

interface PropsModalConversacion {
  lead:     Lead & { pregunta_sondeo?: string | null; propuesta_generada?: string | null };
  onCerrar: () => void;
}

function BurbujaChat({
  tipo,
  contenido,
  timestamp,
}: {
  tipo:      "sistema" | "cliente";
  contenido: string;
  timestamp: string;
}) {
  const esSistema = tipo === "sistema";
  return (
    <div className={`flex ${esSistema ? "justify-start" : "justify-end"}`}>
      <div
        className={`max-w-[85%] rounded-2xl px-4 py-3 shadow-xs ${
          esSistema
            ? "bg-white text-slate-800 border border-slate-200/80 rounded-tl-xs"
            : "bg-[#d9fdd3] text-slate-800 border border-emerald-100 rounded-tr-xs"
        }`}
      >
        <p className="text-[10px] font-bold mb-1 opacity-60">
          {esSistema ? "⚡ Motor de Leads" : "👤 Prospecto"}
        </p>
        <p className="text-xs leading-relaxed whitespace-pre-wrap font-medium">{contenido}</p>
        <p className="text-[9px] opacity-40 text-right mt-1 font-mono">{timestamp}</p>
      </div>
    </div>
  );
}

export default function ModalConversacion({ lead, onCerrar }: PropsModalConversacion) {
  useEffect(() => {
    const handler = (e: KeyboardEvent) => { if (e.key === "Escape") onCerrar(); };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [onCerrar]);

  const tieneSondeo   = !!(lead as any).pregunta_sondeo;
  const tieneRespuesta = !!(lead.opcion_respondida);
  const tienePropuesta = !!(lead as any).propuesta_generada;

  const hoy   = new Date();
  const hora1 = new Date(hoy.getTime() - 1000 * 60 * 5);
  const hora2 = new Date(hoy.getTime() - 1000 * 60 * 3);
  const hora3 = new Date(hoy.getTime() - 1000 * 60 * 1);

  function fmt(d: Date) {
    return d.toLocaleTimeString("es-CO", { hour: "2-digit", minute: "2-digit" });
  }

  const noHayConversacion = !tieneSondeo && !tieneRespuesta;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-xs p-4"
      onClick={(e) => { if (e.target === e.currentTarget) onCerrar(); }}
    >
      <div className="bg-white border border-slate-200 rounded-3xl shadow-2xl w-full max-w-sm flex flex-col max-h-[85vh] overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        {/* Cabecera Smartphone WhatsApp */}
        <div className="flex items-center gap-3 px-4 py-3.5 border-b border-emerald-700 bg-[#008069] text-white">
          <div className="w-9 h-9 rounded-full bg-emerald-800 flex items-center justify-center text-base border border-emerald-600">
            🏪
          </div>
          <div className="flex-1 min-w-0">
            <p className="font-bold text-xs truncate leading-tight">{lead.nombre_negocio}</p>
            <p className="text-[10px] text-emerald-100/90 truncate capitalize">
              {lead.sector} · {lead.canal.replace("_", " ")}
            </p>
          </div>
          <button
            onClick={onCerrar}
            className="w-7 h-7 rounded-full hover:bg-emerald-800/80 text-white flex items-center justify-center text-sm transition-colors"
          >
            ✕
          </button>
        </div>

        {/* Fondo Chat tipo WhatsApp */}
        <div
          className="flex-1 overflow-y-auto px-3.5 py-4 space-y-3 bg-[#efeae2]"
          style={{ backgroundImage: "radial-gradient(#cbd5e1 1px, transparent 1px)", backgroundSize: "16px 16px" }}
        >
          {noHayConversacion && (
            <div className="text-center py-10 bg-white/80 rounded-2xl p-4 border border-slate-200/60 m-2">
              <p className="text-3xl mb-1">💬</p>
              <p className="text-slate-600 text-xs font-semibold">
                Sin mensajes enviados aún
              </p>
              <p className="text-slate-400 text-[11px] mt-0.5">
                Contacta al lead para iniciar la conversación.
              </p>
            </div>
          )}

          {/* Burbuja 1: Micro-sondeo */}
          {tieneSondeo && (
            <BurbujaChat
              tipo="sistema"
              contenido={(lead as any).pregunta_sondeo}
              timestamp={fmt(hora1)}
            />
          )}

          {/* Burbuja 2: Respuesta */}
          {tieneRespuesta && (
            <BurbujaChat
              tipo="cliente"
              contenido={`${lead.opcion_respondida} 👆`}
              timestamp={fmt(hora2)}
            />
          )}

          {/* Burbuja 3: Propuesta Dapta */}
          {tienePropuesta && (
            <BurbujaChat
              tipo="sistema"
              contenido={(lead as any).propuesta_generada}
              timestamp={fmt(hora3)}
            />
          )}
        </div>

        {/* Footer */}
        <div className="px-4 py-3 bg-slate-50 border-t border-slate-100 flex items-center justify-between text-[11px]">
          <span className="text-slate-400 font-medium">Conversación Simulada</span>
          <button
            onClick={onCerrar}
            className="font-bold text-indigo-600 hover:text-indigo-800"
          >
            Cerrar
          </button>
        </div>
      </div>
    </div>
  );
}
