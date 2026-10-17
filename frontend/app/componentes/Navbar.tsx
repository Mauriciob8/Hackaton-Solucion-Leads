/**
 * Navbar.tsx — Barra superior de control y acciones rápidas
 * ==========================================================
 * Incluye buscador global, selector de entorno Demo/Real,
 * botón de exportación CSV, actualización en vivo y perfil admin.
 */

"use client";

interface PropsNavbar {
  busqueda: string;
  onCambiarBusqueda: (valor: string) => void;
  modoDemo: boolean;
  onToggleModoDemo?: () => void;
  cargando: boolean;
  onRecargar: () => void;
  onExportarCSV: () => void;
}

export default function Navbar({
  busqueda,
  onCambiarBusqueda,
  modoDemo,
  cargando,
  onRecargar,
  onExportarCSV,
}: PropsNavbar) {
  return (
    <header className="h-16 bg-white border-b border-slate-200/90 px-6 flex items-center justify-between sticky top-0 z-10 shadow-xs">
      {/* Buscador global tipo SaaS */}
      <div className="flex-1 max-w-md">
        <div className="relative flex items-center">
          <span className="absolute left-3.5 text-slate-400 text-sm">🔍</span>
          <input
            type="text"
            value={busqueda}
            onChange={(e) => onCambiarBusqueda(e.target.value)}
            placeholder="Buscar prospecto, sector, ciudad o señal..."
            className="w-full bg-slate-50 border border-slate-200/80 rounded-xl pl-9 pr-4 py-2 text-xs text-slate-700 placeholder:text-slate-400 focus:outline-none focus:bg-white focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 transition-all duration-150"
          />
          <kbd className="absolute right-3 hidden sm:inline-block px-1.5 py-0.5 text-[10px] font-semibold text-slate-400 bg-white border border-slate-200 rounded">
            /
          </kbd>
        </div>
      </div>

      {/* Controles y Acciones Rápidas */}
      <div className="flex items-center gap-3">
        {/* Chip de Entorno */}
        <div className="flex items-center gap-1.5 bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-xs">
          <span
            className={`w-2 h-2 rounded-full ${
              modoDemo ? "bg-amber-500" : "bg-emerald-500"
            }`}
          />
          <span className="font-medium text-slate-600">
            {modoDemo ? "Modo Demo" : "Modo Real"}
          </span>
          <span className="text-[10px] text-slate-400 font-mono">
            {modoDemo ? "(195 leads)" : "(En vivo)"}
          </span>
        </div>

        {/* Botón Exportar CSV */}
        <button
          onClick={onExportarCSV}
          className="flex items-center gap-1.5 text-xs font-semibold bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-200 px-3 py-1.5 rounded-lg transition-colors duration-150 shadow-2xs"
          title="Descargar todos los prospectos calificados por Dapta en CSV"
        >
          <span>⬇️</span>
          <span>Exportar CSV</span>
        </button>

        {/* Botón Actualizar */}
        <button
          onClick={onRecargar}
          disabled={cargando}
          className="flex items-center gap-1.5 text-xs font-medium bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 px-3 py-1.5 rounded-lg transition-colors duration-150 disabled:opacity-50 shadow-2xs"
        >
          <span>{cargando ? "⏳" : "🔄"}</span>
          <span>Actualizar</span>
        </button>

        {/* Separador */}
        <div className="h-6 w-px bg-slate-200 mx-1" />

        {/* Avatar / Perfil Admin */}
        <div className="flex items-center gap-2 pl-1">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-slate-800 to-indigo-900 text-white font-bold text-xs flex items-center justify-center border border-slate-200 shadow-2xs">
            DP
          </div>
          <div className="hidden lg:block text-left">
            <p className="text-xs font-bold text-slate-800 leading-none">
              Dapta Admin
            </p>
            <p className="text-[10px] text-slate-400 font-medium mt-0.5">
              Equipo Comercial
            </p>
          </div>
        </div>
      </div>
    </header>
  );
}
