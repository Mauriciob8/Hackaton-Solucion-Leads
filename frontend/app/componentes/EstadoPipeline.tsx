/**
 * EstadoPipeline.tsx — Funnel visual de conversión (Estilo AdminKit / Sneat)
 * =========================================================================
 * Embudo limpio en tarjetas blancas con barras de progreso y porcentajes.
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

const CONFIG_ETAPAS: Record<string, { borde: string; bgIcono: string; colorTexto: string; barraBg: string }> = {
  Detectados:   { borde: "border-indigo-100",  bgIcono: "bg-indigo-50",  colorTexto: "text-indigo-600",  barraBg: "bg-indigo-500" },
  Contactados:  { borde: "border-amber-100",   bgIcono: "bg-amber-50",   colorTexto: "text-amber-600",   barraBg: "bg-amber-500" },
  Respondieron: { borde: "border-blue-100",    bgIcono: "bg-blue-50",    colorTexto: "text-blue-600",    barraBg: "bg-blue-500" },
  Calificados:  { borde: "border-emerald-100", bgIcono: "bg-emerald-50", colorTexto: "text-emerald-600", barraBg: "bg-emerald-500" },
};

const ICONOS_ETAPA: Record<string, string> = {
  Detectados:   "🎯",
  Contactados:  "📤",
  Respondieron: "💬",
  Calificados:  "✅",
};

export default function EstadoPipeline({ etapas, modoDemo, cargando }: PropsEstadoPipeline) {
  if (cargando) {
    return (
      <div className="bg-white border border-slate-200/90 rounded-2xl p-6 shadow-xs h-72 cargando" />
    );
  }

  if (!etapas || etapas.length === 0) return null;

  const maxCantidad = Math.max(...etapas.map(e => e.cantidad), 1);

  return (
    <div className="bg-white border border-slate-200/90 rounded-2xl p-6 shadow-xs flex flex-col justify-between">
      {/* Encabezado */}
      <div className="flex items-center justify-between mb-5">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-slate-900 font-bold text-base">
              Embudo de Conversión
            </h2>
            <span className="text-[10px] font-semibold bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full">
              Pipeline End-to-End
            </span>
          </div>
          <p className="text-slate-500 text-xs mt-0.5">
            Evolución del prospecto desde el scraping hasta la validación de Dapta
          </p>
        </div>
        {modoDemo && (
          <span className="text-xs bg-amber-50 text-amber-700 border border-amber-200 px-2.5 py-0.5 rounded-full font-medium">
            Muestra Demo
          </span>
        )}
      </div>

      {/* Grid de etapas del embudo */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {etapas.map((etapa, idx) => {
          const conf = CONFIG_ETAPAS[etapa.etapa] || CONFIG_ETAPAS["Detectados"];
          const icono = ICONOS_ETAPA[etapa.etapa] || "📌";
          const anchoPct = Math.max((etapa.cantidad / maxCantidad) * 100, 8);

          return (
            <div
              key={etapa.etapa}
              className={`bg-slate-50/70 border ${conf.borde} rounded-xl p-4 flex flex-col justify-between sombra-card-hover`}
            >
              <div className="flex items-center justify-between">
                <span className={`w-8 h-8 rounded-lg ${conf.bgIcono} flex items-center justify-center text-sm shadow-2xs`}>
                  {icono}
                </span>
                <span className="text-[10px] font-bold text-slate-400">
                  Paso {idx + 1}
                </span>
              </div>

              <div className="mt-3">
                <p className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                  {etapa.etapa}
                </p>
                <p className="text-xl font-extrabold text-slate-900 mt-0.5">
                  {etapa.cantidad.toLocaleString("es-CO")}
                </p>
              </div>

              {/* Barra de progreso */}
              <div className="mt-3">
                <div className="w-full bg-slate-200/80 rounded-full h-1.5 overflow-hidden">
                  <div
                    className={`h-full ${conf.barraBg} rounded-full transition-all duration-700`}
                    style={{ width: `${anchoPct}%` }}
                  />
                </div>
                <div className="flex items-center justify-between mt-1 text-[10px]">
                  <span className="text-slate-400">
                    {idx === 0 ? "Base 100%" : `${etapa.porcentaje.toFixed(1)}% anterior`}
                  </span>
                  <span className={`font-semibold ${conf.colorTexto}`}>
                    {((etapa.cantidad / maxCantidad) * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Nota explicativa al pie */}
      <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
        <span className="flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-indigo-500" />
          Micro-sondeos de 1 clic incrementan la tasa de respuesta inicial a más del 25%
        </span>
        <span className="font-semibold text-slate-700">Dapta Engine</span>
      </div>
    </div>
  );
}
