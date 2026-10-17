/**
 * GraficoCPL.tsx — Tabla comparativa de CPL por canal
 * ====================================================
 * El argumento visual ganador del hackathon: muestra que un canal
 * más caro en envío (WhatsApp) puede tener el menor CPL calificado
 * gracias a su alta tasa de conversión.
 *
 * Sin dependencias de charting externas — usa CSS puro para las barras.
 */

"use client";

// ---------------------------------------------------------------------------
// Tipos
// ---------------------------------------------------------------------------

export interface MetricaCanal {
  nombre:               string;
  canal_id:             string;
  total_detectados:     number;
  total_contactados:    number;
  total_respondieron:   number;
  total_calificados:    number;
  costo_operativo_total: number;
  tasa_respuesta:       number;
  tasa_calificacion:    number;
  cpl_bruto:            number;
  cpl_calificado:       number;
  prospectos:           number;
}

interface PropsGraficoCPL {
  canales:   MetricaCanal[];
  modoDemo?: boolean;
  cargando?: boolean;
}


// ---------------------------------------------------------------------------
// Sub-componente: Barra de progreso CSS puro
// ---------------------------------------------------------------------------

function BarraPorcentaje({
  valor,
  max,
  color,
}: {
  valor: number;
  max:   number;
  color: string;
}) {
  const pct = max > 0 ? Math.min((valor / max) * 100, 100) : 0;
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 bg-slate-800 rounded-full h-1.5 overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-700 ${color}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="text-xs text-slate-400 w-8 text-right">
        {valor.toFixed(1)}%
      </span>
    </div>
  );
}


// ---------------------------------------------------------------------------
// Componente principal
// ---------------------------------------------------------------------------

export default function GraficoCPL({ canales, modoDemo, cargando }: PropsGraficoCPL) {
  if (cargando) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-3">
        <div className="h-5 bg-slate-800 rounded w-48 cargando" />
        {[...Array(3)].map((_, i) => (
          <div key={i} className="h-12 bg-slate-800/50 rounded cargando" />
        ))}
      </div>
    );
  }

  if (!canales || canales.length === 0) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 text-center text-slate-500">
        Sin datos de canales disponibles
      </div>
    );
  }

  // Encontrar el canal ganador (menor CPL calificado > 0)
  const canalesActivos = canales.filter(c => c.cpl_calificado > 0);
  const cplMinimo = canalesActivos.length > 0
    ? Math.min(...canalesActivos.map(c => c.cpl_calificado))
    : 0;

  const maxTasaRespuesta = Math.max(...canales.map(c => c.tasa_respuesta), 1);
  const maxTasaCalif     = Math.max(...canales.map(c => c.tasa_calificacion), 1);

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
      {/* Encabezado */}
      <div className="flex items-center justify-between mb-5">
        <div>
          <h2 className="text-slate-100 font-semibold text-base">
            Comparativa de CPL por Canal
          </h2>
          <p className="text-slate-400 text-xs mt-0.5">
            CPL Bruto vs. CPL Calificado — Calculado sobre costos reales del sistema
          </p>
        </div>
        {modoDemo && (
          <span className="text-xs bg-amber-500/10 text-amber-400 border border-amber-500/20 px-2 py-1 rounded-full">
            Modo demo
          </span>
        )}
      </div>

      {/* Tabla */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-800/60 text-slate-400 uppercase text-xs">
            <tr>
              <th className="py-3 px-4 rounded-l-lg">Canal</th>
              <th className="py-3 px-4 text-right">Prospectos</th>
              <th className="py-3 px-4 text-right">Calificados</th>
              <th className="py-3 px-4">Tasa Respuesta</th>
              <th className="py-3 px-4 text-right">CPL Bruto</th>
              <th className="py-3 px-4 text-right rounded-r-lg">CPL Calificado</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {canales.map((canal) => {
              const esGanador = canal.cpl_calificado > 0 && canal.cpl_calificado === cplMinimo;
              return (
                <tr
                  key={canal.canal_id}
                  className={`hover:bg-slate-800/30 transition-colors ${
                    esGanador ? "bg-emerald-950/20" : ""
                  }`}
                >
                  {/* Nombre del canal */}
                  <td className="py-4 px-4">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-slate-100">{canal.nombre}</span>
                      {esGanador && (
                        <span className="text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-1.5 py-0.5 rounded-full">
                          ⭐ Mejor CPL
                        </span>
                      )}
                    </div>
                  </td>

                  {/* Total prospectos */}
                  <td className="py-4 px-4 text-right text-slate-300">
                    {canal.total_detectados.toLocaleString("es-CO")}
                  </td>

                  {/* Calificados */}
                  <td className="py-4 px-4 text-right">
                    <span className="text-emerald-400 font-semibold">
                      {canal.total_calificados}
                    </span>
                  </td>

                  {/* Tasa de respuesta con barra */}
                  <td className="py-4 px-4 min-w-[140px]">
                    <BarraPorcentaje
                      valor={canal.tasa_respuesta}
                      max={maxTasaRespuesta}
                      color="bg-blue-500"
                    />
                  </td>

                  {/* CPL Bruto */}
                  <td className="py-4 px-4 text-right text-amber-400">
                    {canal.cpl_bruto > 0 ? `$${canal.cpl_bruto.toFixed(4)}` : "—"}
                  </td>

                  {/* CPL Calificado */}
                  <td className="py-4 px-4 text-right">
                    <span
                      className={`font-bold text-base ${
                        esGanador ? "text-emerald-400" : "text-slate-100"
                      }`}
                    >
                      {canal.cpl_calificado > 0
                        ? `$${canal.cpl_calificado.toFixed(2)}`
                        : "—"}
                    </span>
                    <span className="text-slate-500 text-xs ml-1">USD</span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Insight clave */}
      <div className="mt-5 p-3 bg-indigo-950/40 border border-indigo-500/20 rounded-lg">
        <p className="text-indigo-300 text-xs">
          💡 <strong>Insight clave:</strong> Un canal con mayor costo de envío (WhatsApp: ~$0.035 USD)
          puede generar el <strong>menor CPL calificado</strong> gracias a su alta tasa de conversión.
          El costo que importa no es el del mensaje, sino el del lead que realmente convierte.
        </p>
      </div>
    </div>
  );
}
