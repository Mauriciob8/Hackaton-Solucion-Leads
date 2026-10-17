/**
 * TarjetaResumen.tsx — KPI Cards del dashboard
 * =============================================
 * Muestra las métricas más importantes en tarjetas visuales:
 * Total leads, leads calificados, mejor CPL y tasa de respuesta promedio.
 */

"use client";

interface PropsKPI {
  titulo:     string;
  valor:      string;
  subtitulo?: string;
  color:      "indigo" | "emerald" | "amber" | "blue";
  icono:      string;  // Emoji como ícono liviano (sin dependencias)
}

/** Mapa de clases Tailwind por color — evita purga de CSS */
const ESTILOS_COLOR: Record<PropsKPI["color"], { borde: string; texto: string; fondo: string }> = {
  indigo:  { borde: "border-indigo-500/30",  texto: "text-indigo-400",  fondo: "bg-indigo-500/10" },
  emerald: { borde: "border-emerald-500/30", texto: "text-emerald-400", fondo: "bg-emerald-500/10" },
  amber:   { borde: "border-amber-500/30",   texto: "text-amber-400",   fondo: "bg-amber-500/10" },
  blue:    { borde: "border-blue-500/30",    texto: "text-blue-400",    fondo: "bg-blue-500/10" },
};

/** Una sola tarjeta KPI */
function TarjetaKPI({ titulo, valor, subtitulo, color, icono }: PropsKPI) {
  const estilos = ESTILOS_COLOR[color];
  return (
    <div
      className={`
        bg-slate-900 border ${estilos.borde} rounded-xl p-5
        flex items-start gap-4 shadow-lg
        hover:bg-slate-800/60 transition-colors duration-200
      `}
    >
      {/* Ícono */}
      <div className={`${estilos.fondo} ${estilos.borde} border rounded-lg p-2.5 text-2xl leading-none`}>
        {icono}
      </div>

      {/* Datos */}
      <div className="flex-1 min-w-0">
        <p className="text-slate-400 text-xs font-medium uppercase tracking-wider truncate">
          {titulo}
        </p>
        <p className={`${estilos.texto} text-2xl font-bold mt-0.5`}>
          {valor}
        </p>
        {subtitulo && (
          <p className="text-slate-500 text-xs mt-1">{subtitulo}</p>
        )}
      </div>
    </div>
  );
}


// ---------------------------------------------------------------------------
// Props del componente principal
// ---------------------------------------------------------------------------

export interface DatosResumen {
  total_leads_sistema: number;
  total_calificados:   number;
  costo_total_usd:     number;
  cpl_promedio_global: number;
  canal_mas_eficiente: string;
  mejor_cpl_calificado: number;
}

interface PropsTarjetaResumen {
  datos:     DatosResumen;
  cargando?: boolean;
}


// ---------------------------------------------------------------------------
// Componente principal
// ---------------------------------------------------------------------------

export default function TarjetaResumen({ datos, cargando }: PropsTarjetaResumen) {
  if (cargando) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <div
            key={i}
            className="bg-slate-900 border border-slate-800 rounded-xl p-5 h-28 cargando"
          />
        ))}
      </div>
    );
  }

  // Calcular tasa de calificación global
  const tasaCalif =
    datos.total_leads_sistema > 0
      ? ((datos.total_calificados / datos.total_leads_sistema) * 100).toFixed(1)
      : "0.0";

  const kpis: PropsKPI[] = [
    {
      titulo:    "Leads Detectados",
      valor:     datos.total_leads_sistema.toLocaleString("es-CO"),
      subtitulo: "Pymes con señal de dolor real",
      color:     "indigo",
      icono:     "🎯",
    },
    {
      titulo:    "Leads Calificados Dapta",
      valor:     datos.total_calificados.toLocaleString("es-CO"),
      subtitulo: `${tasaCalif}% de tasa de calificación`,
      color:     "emerald",
      icono:     "✅",
    },
    {
      titulo:    "Mejor CPL Calificado",
      valor:     datos.mejor_cpl_calificado > 0 ? `$${datos.mejor_cpl_calificado.toFixed(2)} USD` : "—",
      subtitulo: datos.canal_mas_eficiente || "Sin datos suficientes",
      color:     "amber",
      icono:     "💰",
    },
    {
      titulo:    "Gasto Total del Sistema",
      valor:     `$${datos.costo_total_usd.toFixed(3)} USD`,
      subtitulo: `CPL prom. $${datos.cpl_promedio_global.toFixed(2)} USD`,
      color:     "blue",
      icono:     "📊",
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {kpis.map((kpi) => (
        <TarjetaKPI key={kpi.titulo} {...kpi} />
      ))}
    </div>
  );
}
