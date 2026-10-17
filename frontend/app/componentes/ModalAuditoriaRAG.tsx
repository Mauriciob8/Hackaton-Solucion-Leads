/**
 * ModalAuditoriaRAG.tsx — Modal de trazabilidad RAG (Estilo Admin Profesional)
 * ============================================================================
 * Muestra el desglose del razonamiento:
 * 1. Fragmento público detectado
 * 2. Documento consultado en el catálogo Dapta
 * 3. Mensaje final generado
 * 4. Costos atómicos de auditoría
 */

"use client";

import { useEffect, useState } from "react";

interface FragmentoDetectado {
  texto:            string;
  tipo_senal:       string;
  fuente_deteccion: string;
}

interface SolucionConsultada {
  id:                     string | null;
  titulo:                 string;
  categoria:              string | null;
  caso_exito:             string | null;
  resultado_tipico:       string | null;
  precio_referencial_usd: number | null;
}

interface Conversacion {
  pregunta_sondeo:    string;
  opcion_respondida:  string;
  propuesta_generada: string;
}

interface CostosAuditoria {
  costo_scraping_usd: number;
  costo_tokens_usd:   number;
  costo_envio_usd:    number;
  costo_total_usd:    number;
}

interface DatosAuditoria {
  lead_id:             string;
  nombre_negocio:      string;
  sector:              string;
  estado_actual:       string;
  fragmento_detectado: FragmentoDetectado;
  solucion_consultada: SolucionConsultada;
  conversacion:        Conversacion;
  costos_auditoria:    CostosAuditoria;
}

interface PropsModalAuditoria {
  leadId:    string;
  apiUrl:    string;
  onCerrar:  () => void;
}

export default function ModalAuditoriaRAG({ leadId, apiUrl, onCerrar }: PropsModalAuditoria) {
  const [datos, setDatos] = useState<DatosAuditoria | null>(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function cargar() {
      try {
        const res = await fetch(`${apiUrl}/api/leads/${leadId}/auditoria`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        setDatos(data);
      } catch {
        setError("No se pudo cargar la auditoría del lead.");
      } finally {
        setCargando(false);
      }
    }
    cargar();
  }, [leadId, apiUrl]);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => { if (e.key === "Escape") onCerrar(); };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [onCerrar]);

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-xs p-4"
      onClick={(e) => { if (e.target === e.currentTarget) onCerrar(); }}
    >
      <div className="bg-white border border-slate-200 rounded-3xl shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        {/* Cabecera */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100 bg-slate-50/50">
          <div>
            <div className="flex items-center gap-2">
              <span className="w-7 h-7 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center font-bold text-sm">
                🔍
              </span>
              <h2 className="text-slate-900 font-extrabold text-base">
                Inspección y Auditoría RAG
              </h2>
            </div>
            {datos && (
              <p className="text-slate-500 text-xs mt-0.5 ml-9">
                {datos.nombre_negocio} · Sector: {datos.sector}
              </p>
            )}
          </div>
          <button
            onClick={onCerrar}
            className="w-8 h-8 rounded-full hover:bg-slate-100 text-slate-400 hover:text-slate-700 flex items-center justify-center text-lg transition-colors"
          >
            ✕
          </button>
        </div>

        {/* Cuerpo */}
        <div className="overflow-y-auto flex-1 px-6 py-5 space-y-4">
          {cargando && (
            <div className="space-y-3">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="h-24 bg-slate-50 rounded-2xl cargando" />
              ))}
            </div>
          )}

          {error && (
            <div className="bg-rose-50 border border-rose-200 rounded-2xl p-4 text-rose-700 text-xs">
              ⚠️ {error}
            </div>
          )}

          {datos && (
            <>
              {/* Bloque 1 */}
              <div className="border border-indigo-100 rounded-2xl p-4 bg-indigo-50/20">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-[10px] font-bold bg-indigo-600 text-white px-2 py-0.5 rounded-full">
                    1
                  </span>
                  <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wide">
                    Señal Pública Detectada
                  </h3>
                </div>
                <p className="text-slate-700 text-xs bg-white rounded-xl p-3 border border-indigo-100 italic leading-relaxed">
                  &ldquo;{datos.fragmento_detectado.texto}&rdquo;
                </p>
                <div className="flex gap-2 mt-2">
                  <span className="text-[10px] font-semibold text-indigo-700 bg-indigo-50 border border-indigo-100 px-2 py-0.5 rounded-md capitalize">
                    {datos.fragmento_detectado.tipo_senal.replace(/_/g, " ")}
                  </span>
                  <span className="text-[10px] font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded-md capitalize">
                    Fuente: {datos.fragmento_detectado.fuente_deteccion.replace(/_/g, " ")}
                  </span>
                </div>
              </div>

              {/* Bloque 2 */}
              <div className="border border-amber-100 rounded-2xl p-4 bg-amber-50/20">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-[10px] font-bold bg-amber-600 text-white px-2 py-0.5 rounded-full">
                    2
                  </span>
                  <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wide">
                    Ficha del Catálogo Dapta Consultada
                  </h3>
                </div>
                <div className="bg-white rounded-xl p-3 border border-amber-100 space-y-2">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono font-bold bg-amber-50 text-amber-700 px-2 py-0.5 rounded">
                      {datos.solucion_consultada.id ?? "—"}
                    </span>
                    <span className="text-slate-900 font-bold text-xs">
                      {datos.solucion_consultada.titulo}
                    </span>
                  </div>
                  {datos.solucion_consultada.resultado_tipico && (
                    <p className="text-emerald-700 text-xs font-medium">
                      ✅ {datos.solucion_consultada.resultado_tipico}
                    </p>
                  )}
                  {datos.solucion_consultada.caso_exito && (
                    <p className="text-slate-600 text-xs bg-slate-50 rounded-lg p-2 border border-slate-100">
                      📋 Caso Real: {datos.solucion_consultada.caso_exito}
                    </p>
                  )}
                </div>
              </div>

              {/* Bloque 3 */}
              <div className="border border-emerald-100 rounded-2xl p-4 bg-emerald-50/20">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-[10px] font-bold bg-emerald-600 text-white px-2 py-0.5 rounded-full">
                    3
                  </span>
                  <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wide">
                    Mensajes y Respuesta Registrada
                  </h3>
                </div>
                <div className="bg-white rounded-xl p-3 border border-emerald-100 space-y-3">
                  <div>
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wide">Micro-Sondeo:</span>
                    <p className="text-slate-700 text-xs mt-0.5 whitespace-pre-wrap leading-relaxed">
                      {datos.conversacion.pregunta_sondeo}
                    </p>
                  </div>
                  {datos.conversacion.opcion_respondida !== "Sin respuesta" && (
                    <div className="flex items-center gap-2 pt-2 border-t border-slate-100">
                      <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wide">Elección:</span>
                      <span className="text-xs font-bold bg-blue-50 text-blue-700 border border-blue-200 px-2 py-0.5 rounded">
                        Opción {datos.conversacion.opcion_respondida}
                      </span>
                    </div>
                  )}
                  {datos.conversacion.propuesta_generada !== "Propuesta aún no generada" && (
                    <div className="pt-2 border-t border-slate-100">
                      <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wide">Propuesta Enviada:</span>
                      <p className="text-slate-700 text-xs mt-0.5 whitespace-pre-wrap leading-relaxed bg-slate-50 p-2.5 rounded-lg border border-slate-100">
                        {datos.conversacion.propuesta_generada}
                      </p>
                    </div>
                  )}
                </div>
              </div>

              {/* Costos Atómicos */}
              <div className="bg-slate-50 rounded-2xl p-4 border border-slate-200/80">
                <p className="text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-2">
                  Trazabilidad de Costos Atómicos
                </p>
                <div className="grid grid-cols-4 gap-2 text-center">
                  {[
                    { label: "Scraping",  val: datos.costos_auditoria.costo_scraping_usd },
                    { label: "Tokens LLM", val: datos.costos_auditoria.costo_tokens_usd },
                    { label: "Envío",      val: datos.costos_auditoria.costo_envio_usd },
                    { label: "Total",      val: datos.costos_auditoria.costo_total_usd },
                  ].map(({ label, val }) => (
                    <div key={label} className="bg-white p-2 rounded-xl border border-slate-200/60 shadow-2xs">
                      <p className="text-indigo-600 font-mono font-bold text-xs">${val.toFixed(4)}</p>
                      <p className="text-slate-400 text-[10px] font-medium mt-0.5">{label}</p>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-slate-100 bg-slate-50/50 flex justify-end">
          <button
            onClick={onCerrar}
            className="text-xs font-semibold bg-white hover:bg-slate-100 text-slate-700 border border-slate-200 px-4 py-2 rounded-xl transition-colors shadow-2xs"
          >
            Cerrar
          </button>
        </div>
      </div>
    </div>
  );
}
