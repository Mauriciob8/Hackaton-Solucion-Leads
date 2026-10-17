/**
 * TarjetaResumen.tsx — KPI Cards del dashboard (Estilo Sneat / AdminKit Pro)
 * =========================================================================
 * Muestra las métricas más importantes en tarjetas blancas pulidas,
 * con iconos en contenedores de color suave y tipografía corporativa.
 */

"use client";

interface PropsKPI {
  titulo:     string;
  valor:      string;
  subtitulo?: string;
  color:      "indigo" | "emerald" | "amber" | "blue";
  icono:      string;
  badge?:     string;
}

const ESTILOS_COLOR: Record<PropsKPI["color"], { fondoIcono: string; textoIcono: string; badgeClase: string }> = {
  indigo:  { fondoIcono: "bg-indigo-50",  textoIcono: "text-indigo-600", badgeClase: "bg-indigo-50 text-indigo-700 border-indigo-100" },
  emerald: { fondoIcono: "bg-emerald-50", textoIcono: "text-emerald-600", badgeClase: "bg-emerald-50 text-emerald-700 border-emerald-100" },
  amber:   { fondoIcono: "bg-amber-50",   textoIcono: "text-amber-600", badgeClase: "bg-amber-50 text-amber-700 border-amber-100" },
  blue:    { fondoIcono: "bg-blue-50",    textoIcono: "text-blue-600", badgeClase: "bg-blue-50 text-blue-700 border-blue-100" },
};

function TarjetaKPI({ titulo, valor, subtitulo, color, icono, badge }: PropsKPI) {
  const estilos = ESTILOS_COLOR[color];
  return (
    <div className="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-xs sombra-card-hover flex flex-col justify-between">
      <div className="flex items-start justify-between">
        <div className={`w-11 h-11 rounded-xl ${estilos.fondoIcono} flex items-center justify-center text-xl`}>
          {icono}
        </div>
        {badge && (
          <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${estilos.badgeClase}`}>
            {badge}
          </span>
        )}
      </div>

      <div className="mt-4">
        <p className="text-slate-500 text-xs font-semibold uppercase tracking-wider">
          {titulo}
        </p>
        <p className="text-slate-900 text-2xl font-extrabold mt-1 tracking-tight">
          {valor}
        </p>
        {subtitulo && (
          <p className="text-slate-400 text-xs font-medium mt-1">
            {subtitulo}
          </p>
        )}
      </div>
    </div>
  );
}

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

export default function TarjetaResumen({ datos, cargando }: PropsTarjetaResumen) {
  if (cargando) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <div
            key={i}
            className="bg-white border border-slate-200 rounded-2xl p-5 h-32 cargando shadow-xs"
          />
        ))}
      </div>
    );
  }

  const tasaCalif =
    datos.total_leads_sistema > 0
      ? ((datos.total_calificados / datos.total_leads_sistema) * 100).toFixed(1)
      : "0.0";

  const kpis: PropsKPI[] = [
    {
      titulo:    "Leads Detectados",
      valor:     datos.total_leads_sistema.toLocaleString("es-CO"),
      subtitulo: "Señales de dolor en Maps, Empleo y Web",
      color:     "indigo",
      icono:     "🎯",
      badge:     "100% Gratis",
    },
    {
      titulo:    "Leads Calificados",
      valor:     datos.total_calificados.toLocaleString("es-CO"),
      subtitulo: `${tasaCalif}% de tasa de aprobación`,
      color:     "emerald",
      icono:     "✅",
      badge:     "Dapta Score ≥ 0.6",
    },
    {
      titulo:    "Mejor CPL Calificado",
      valor:     datos.mejor_cpl_calificado > 0 ? `$${datos.mejor_cpl_calificado.toFixed(2)} USD` : "—",
      subtitulo: datos.canal_mas_eficiente || "Sin datos suficientes",
      color:     "amber",
      icono:     "💰",
      badge:     "Más Rentable",
    },
    {
      titulo:    "Gasto Total Operativo",
      valor:     `$${datos.costo_total_usd.toFixed(3)} USD`,
      subtitulo: `CPL prom. $${datos.cpl_promedio_global.toFixed(2)} USD`,
      color:     "blue",
      icono:     "📊",
      badge:     "Tokens + Envíos",
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
