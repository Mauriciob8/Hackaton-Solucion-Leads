/**
 * EstadoPipeline.tsx — Funnel visual de conversión
 * =================================================
 * Muestra el flujo completo del lead desde detección hasta calificación:
 * Detectados → Contactados → Respondieron → Calificados
 *
 * Implementación visual pura con CSS (sin librerías de gráficos).
 */

"use client";

export interface DatoFunnel {
  etapa:       string;
  cantidad:    number;
  porcentaje:  number;
  color:       string;
}

interface PropsEstadoPipeline {
  etapas:    DatoFunnel[];
  modoDemo?: boolean;
  cargando?: boolean;
}

// Mapas de clases Tailwind para cada etapa (colores pre-definidos)
const CLASES_ETAPA: Record<string, { borde: string; fondo: string; texto: string; barra: string }> = {
  Detectados:   { borde: "border-indigo-500/40", fondo: "bg-indigo-500/10", texto: "text-indigo-300", barra: "bg-indigo-500" },
  Contactados:  { borde: "border-amber-500/40",  fondo: "bg-amber-500/10",  texto: "text-amber-300",  barra: "bg-amber-500" },
  Respondieron: { borde: "border-blue-500/40",   fondo: "bg-blue-500/10",   texto: "text-blue-300",   barra: "bg-blue-500" },
  Calificados:  { borde: "border-emerald-500/40",fondo: "bg-emerald-500/10",texto: "text-emerald-300",barra: "bg-emerald-500" },
};

const ICONOS_ETAPA: Record<string, string> = {
  Detectados:   "🔍",
  Contactados:  "📤",
  Respondieron: "💬",
  Calificados:  "✅",
};

export default function EstadoPipeline({ etapas, modoDemo, cargando }: PropsEstadoPipeline) {
  if (cargando) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
        <div className="h-5 bg-slate-800 rounded w-36 mb-4 cargando" />
        <div className="flex gap-3">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="flex-1 h-24 bg-slate-800 rounded-lg cargando" />
          ))}
        </div>
      </div>
    );
  }

  if (!etapas || etapas.length === 0) return null;

  const maxCantidad = Math.max(...etapas.map(e => e.cantidad), 1);

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
      {/* Encabezado */}
      <div className="flex items-center justify-between mb-5">
        <div>
          <h2 className="text-slate-100 font-semibold text-base">
            Funnel de Conversión
          </h2>
          <p className="text-slate-400 text-xs mt-0.5">
            Tasa de conversión entre etapas del pipeline
          </p>
        </div>
        {modoDemo && (
          <span className="text-xs bg-amber-500/10 text-amber-400 border border-amber-500/20 px-2 py-1 rounded-full">
            Modo demo
          </span>
        )}
      </div>

      {/* Tarjetas del funnel */}
      <div className="flex flex-col sm:flex-row gap-2 sm:gap-0 items-stretch">
        {etapas.map((etapa, idx) => {
          const clases = CLASES_ETAPA[etapa.etapa] || CLASES_ETAPA["Detectados"];
          const icono  = ICONOS_ETAPA[etapa.etapa] || "📌";
          const anchoPct = Math.max((etapa.cantidad / maxCantidad) * 100, 10);

          return (
            <div key={etapa.etapa} className="flex flex-row sm:flex-col items-center flex-1">
              {/* Tarjeta de etapa */}
              <div
                className={`
                  flex-1 sm:w-full border ${clases.borde} ${clases.fondo}
                  rounded-xl p-4 flex flex-col items-center gap-2
                  min-w-0 transition-transform hover:scale-105 duration-200
                `}
              >
                <span className="text-2xl">{icono}</span>
                <p className="text-slate-400 text-xs text-center font-medium uppercase tracking-wide">
                  {etapa.etapa}
                </p>
                <p className={`${clases.texto} text-2xl font-bold`}>
                  {etapa.cantidad.toLocaleString("es-CO")}
                </p>
                {/* Barra de conversión */}
                <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                  <div
                    className={`h-full ${clases.barra} rounded-full transition-all duration-700`}
                    style={{ width: `${anchoPct}%` }}
                  />
                </div>
                {idx > 0 && (
                  <p className="text-slate-500 text-xs">
                    {etapa.porcentaje.toFixed(1)}% de anterior
                  </p>
                )}
              </div>

              {/* Flecha entre etapas */}
              {idx < etapas.length - 1 && (
                <div className="hidden sm:flex items-center justify-center w-6 flex-shrink-0">
                  <span className="text-slate-600 text-lg">→</span>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
