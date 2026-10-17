/**
 * TarjetaSmartRouter.tsx — Recomendador predictivo de canales (Estilo Admin)
 * =========================================================================
 * Banner corporativo con recomendación estratégica basada en CPL real.
 */

"use client";

export interface DatosSmartRouter {
  hay_recomendacion:       boolean;
  canal_recomendado?:      string;
  canal_recomendado_id?:   string;
  cpl_recomendado?:        number;
  canal_alternativo?:      string;
  cpl_alternativo?:        number;
  ahorro_porcentual?:      number | null;
  total_canales_comparados?: number;
  mensaje:                 string;
  modo_demo:               boolean;
}

interface PropsTarjetaSmartRouter {
  datos:     DatosSmartRouter | null;
  cargando?: boolean;
}

const ICONOS_CANAL: Record<string, string> = {
  email:          "📧",
  whatsapp:       "💬",
  formulario_web: "🌐",
};

export default function TarjetaSmartRouter({ datos, cargando }: PropsTarjetaSmartRouter) {
  if (cargando) {
    return (
      <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs cargando h-28" />
    );
  }

  if (!datos) return null;

  if (!datos.hay_recomendacion) {
    return (
      <div className="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-xs flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-slate-100 flex items-center justify-center text-xl">
            🤖
          </div>
          <div>
            <h3 className="text-slate-800 font-bold text-xs uppercase tracking-wide">
              Smart Router — Recomendador Predictivo
            </h3>
            <p className="text-slate-500 text-xs mt-0.5">{datos.mensaje}</p>
          </div>
        </div>
      </div>
    );
  }

  const iconoCanal = ICONOS_CANAL[datos.canal_recomendado_id ?? ""] ?? "⚡";

  return (
    <div className="bg-gradient-to-r from-white via-indigo-50/20 to-indigo-50/50 border border-indigo-200/80 rounded-2xl p-5 shadow-xs">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Lado izquierdo: Canal recomendado y mensaje */}
        <div className="flex items-start gap-3.5">
          <div className="w-12 h-12 rounded-xl bg-indigo-600 text-white flex items-center justify-center text-2xl shadow-md shadow-indigo-600/20 flex-shrink-0">
            {iconoCanal}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[11px] font-bold text-indigo-700 bg-indigo-100/70 border border-indigo-200 px-2 py-0.5 rounded-full uppercase tracking-wider">
                Recomendación de Presupuesto
              </span>
              <span className="text-xs text-slate-400">
                Basado en {datos.total_canales_comparados ?? 3} canales
              </span>
            </div>
            <h3 className="text-slate-900 font-extrabold text-base mt-1">
              Canal Óptimo: {datos.canal_recomendado}
            </h3>
            <p className="text-slate-600 text-xs mt-1 leading-relaxed max-w-2xl">
              {datos.mensaje}
            </p>
          </div>
        </div>

        {/* Lado derecho: Métrica de Ahorro */}
        {datos.ahorro_porcentual !== null && datos.ahorro_porcentual !== undefined && (
          <div className="flex items-center gap-3 bg-white border border-emerald-200 rounded-xl px-4 py-3 shadow-xs flex-shrink-0 self-start md:self-auto">
            <div className="w-10 h-10 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center text-xl font-bold">
              💰
            </div>
            <div>
              <div className="flex items-baseline gap-1">
                <span className="text-emerald-600 font-extrabold text-xl">
                  -{datos.ahorro_porcentual}%
                </span>
                <span className="text-slate-400 text-[10px] font-medium">CPL</span>
              </div>
              <p className="text-slate-500 text-[11px] font-medium">
                vs. {datos.canal_alternativo}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
