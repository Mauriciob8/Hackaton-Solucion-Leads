/**
 * GraficoCPL.tsx — Tabla comparativa de CPL por canal (Estilo AdminKit Pro)
 * =========================================================================
 * Muestra la rentabilidad real de cada canal de contacto (Email, WhatsApp, Formulario).
 */

"use client";

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
      <div className="flex-1 bg-slate-100 rounded-full h-1.5 overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-700 ${color}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="text-xs font-semibold text-slate-700 w-9 text-right font-mono">
        {valor.toFixed(1)}%
      </span>
    </div>
  );
}

const ICONOS_CANAL: Record<string, string> = {
  email:          "📧",
  whatsapp:       "💬",
  formulario_web: "🌐",
};

export default function GraficoCPL({ canales, modoDemo, cargando }: PropsGraficoCPL) {
  if (cargando) {
    return (
      <div className="bg-white border border-slate-200/90 rounded-2xl p-6 shadow-xs h-72 cargando" />
    );
  }

  if (!canales || canales.length === 0) {
    return (
      <div className="bg-white border border-slate-200/90 rounded-2xl p-6 text-center text-slate-400">
        Sin datos de canales disponibles
      </div>
    );
  }

  const canalesActivos = canales.filter(c => c.cpl_calificado > 0);
  const cplMinimo = canalesActivos.length > 0
    ? Math.min(...canalesActivos.map(c => c.cpl_calificado))
    : 0;

  const maxTasaRespuesta = Math.max(...canales.map(c => c.tasa_respuesta), 1);

  return (
    <div className="bg-white border border-slate-200/90 rounded-2xl p-6 shadow-xs flex flex-col justify-between">
      {/* Encabezado */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-slate-900 font-bold text-base">
              Unit Economics por Canal
            </h2>
            <span className="text-[10px] font-semibold bg-indigo-50 text-indigo-700 border border-indigo-100 px-2 py-0.5 rounded-full">
              CPL Real
            </span>
          </div>
          <p className="text-slate-500 text-xs mt-0.5">
            Costo marginal por prospecto calificado según inversión atómica registrada
          </p>
        </div>
        {modoDemo && (
          <span className="text-xs bg-amber-50 text-amber-700 border border-amber-200 px-2.5 py-0.5 rounded-full font-medium">
            Demo
          </span>
        )}
      </div>

      {/* Tabla de canales */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="border-b border-slate-200 text-slate-400 uppercase tracking-wider font-semibold text-[10px]">
              <th className="py-2.5 px-3">Canal</th>
              <th className="py-2.5 px-3 text-right">Prospectos</th>
              <th className="py-2.5 px-3 text-right">Aprobados</th>
              <th className="py-2.5 px-3">Tasa Respuesta</th>
              <th className="py-2.5 px-3 text-right">CPL Bruto</th>
              <th className="py-2.5 px-3 text-right">CPL Calificado</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {canales.map((canal) => {
              const esGanador = canal.cpl_calificado > 0 && canal.cpl_calificado === cplMinimo;
              const icono = ICONOS_CANAL[canal.canal_id] || "📡";

              return (
                <tr
                  key={canal.canal_id}
                  className={`hover:bg-slate-50/80 transition-colors ${
                    esGanador ? "bg-emerald-50/40" : ""
                  }`}
                >
                  {/* Nombre */}
                  <td className="py-3 px-3">
                    <div className="flex items-center gap-2">
                      <span className="text-base">{icono}</span>
                      <span className="font-bold text-slate-800">{canal.nombre}</span>
                      {esGanador && (
                        <span className="text-[10px] bg-emerald-100 text-emerald-800 border border-emerald-200 px-1.5 py-0.2 rounded font-bold">
                          Mejor ROI
                        </span>
                      )}
                    </div>
                  </td>

                  {/* Prospectos */}
                  <td className="py-3 px-3 text-right text-slate-600 font-medium">
                    {canal.total_detectados.toLocaleString("es-CO")}
                  </td>

                  {/* Aprobados */}
                  <td className="py-3 px-3 text-right font-bold text-emerald-600">
                    {canal.total_calificados}
                  </td>

                  {/* Tasa respuesta */}
                  <td className="py-3 px-3 min-w-[130px]">
                    <BarraPorcentaje
                      valor={canal.tasa_respuesta}
                      max={maxTasaRespuesta}
                      color="bg-indigo-600"
                    />
                  </td>

                  {/* CPL Bruto */}
                  <td className="py-3 px-3 text-right font-mono text-slate-600">
                    {canal.cpl_bruto > 0 ? `$${canal.cpl_bruto.toFixed(4)}` : "—"}
                  </td>

                  {/* CPL Calificado */}
                  <td className="py-3 px-3 text-right">
                    <span
                      className={`font-extrabold text-sm ${
                        esGanador ? "text-emerald-600" : "text-slate-900"
                      }`}
                    >
                      {canal.cpl_calificado > 0
                        ? `$${canal.cpl_calificado.toFixed(2)}`
                        : "—"}
                    </span>
                    <span className="text-slate-400 text-[10px] ml-1">USD</span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Insight corporativo al pie */}
      <div className="mt-4 p-3 bg-slate-50 border border-slate-200/80 rounded-xl flex items-start gap-2.5">
        <span className="text-base leading-none">💡</span>
        <p className="text-slate-600 text-[11px] leading-relaxed">
          <strong>La Paradoja de WhatsApp:</strong> Aunque enviar por WhatsApp cuesta ~$0.035 USD vs ~$0.0002 de email, su alta tasa de respuesta (28%) reduce el <strong>CPL Calificado un 22%</strong> frente al email frío masivo.
        </p>
      </div>
    </div>
  );
}
