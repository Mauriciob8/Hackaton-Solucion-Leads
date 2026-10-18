/**
 * Sidebar.tsx — Menú lateral moderno de navegación modular
 * ==========================================================
 * Inspirado en la arquitectura visual de AdminKit Pro y Sneat.
 * Divide la plataforma en Operaciones y Rendimiento/Inteligencia,
 * con estado del sistema y credenciales en el pie.
 */

"use client";

export type ModuloActivo =
  | "dashboard"
  | "deteccion"
  | "pipeline"
  | "unit_economics"
  | "catalogo_rag";

interface PropsSidebar {
  moduloActivo: ModuloActivo;
  onCambiarModulo: (modulo: ModuloActivo) => void;
  totalLeads: number;
  totalCalificados: number;
}

export default function Sidebar({
  moduloActivo,
  onCambiarModulo,
  totalLeads,
  totalCalificados,
}: PropsSidebar) {
  const itemsOperaciones = [
    {
      id: "dashboard" as ModuloActivo,
      nombre: "Dashboard General",
      icono: "📊",
      badge: null,
    },
    {
      id: "deteccion" as ModuloActivo,
      nombre: "Detección Activa",
      icono: "🎯",
      badge: "Scraper",
    },
    {
      id: "pipeline" as ModuloActivo,
      nombre: "Pipeline de Leads",
      icono: "🗂️",
      badge: totalLeads > 0 ? totalLeads.toString() : null,
    },
  ];

  const itemsInteligencia = [
    {
      id: "unit_economics" as ModuloActivo,
      nombre: "Unit Economics & CPL",
      icono: "📈",
      badge: "ROI",
    },
    {
      id: "catalogo_rag" as ModuloActivo,
      nombre: "Base RAG (Catálogo)",
      icono: "🤖",
      badge: "Dapta",
    },
  ];

  return (
    <aside className="w-64 bg-white border-r border-slate-200/90 flex flex-col justify-between h-screen sticky top-0 z-20 select-none shadow-[1px_0_4px_rgba(0,0,0,0.02)]">
      {/* 1. Header con Logo */}
      <div>
        <div className="h-16 px-6 flex items-center gap-3 border-b border-slate-100">
          <div className="w-9 h-9 rounded-xl flex items-center justify-center overflow-hidden shadow-xs border border-slate-200/80 bg-white p-1">
            <img
              src="/Logo.ico"
              alt="Logo Motor de Leads"
              className="w-full h-full object-contain"
            />
          </div>
          <div>
            <h1 className="font-bold text-slate-800 text-sm tracking-tight flex items-center gap-1.5">
              Motor de Leads
              <span className="text-[10px] font-semibold bg-indigo-50 text-indigo-600 px-1.5 py-0.5 rounded-md border border-indigo-100">
                v1.2
              </span>
            </h1>
            <p className="text-[11px] text-slate-400 font-medium">
              Intent-Based Lead Engine
            </p>
          </div>
        </div>

        {/* 2. Menú de Navegación */}
        <div className="px-3 py-5 space-y-6 overflow-y-auto max-h-[calc(100vh-14rem)]">
          {/* Sección Operaciones */}
          <div>
            <p className="px-3 text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2">
              Operaciones
            </p>
            <nav className="space-y-1">
              {itemsOperaciones.map((item) => {
                const activo = moduloActivo === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => onCambiarModulo(item.id)}
                    className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl font-medium text-xs transition-all duration-150 ${
                      activo
                        ? "bg-indigo-50 text-indigo-600 shadow-sm border border-indigo-100/80 font-semibold"
                        : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
                    }`}
                  >
                    <div className="flex items-center gap-2.5">
                      <span className="text-base">{item.icono}</span>
                      <span>{item.nombre}</span>
                    </div>
                    {item.badge && (
                      <span
                        className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${
                          activo
                            ? "bg-indigo-600 text-white"
                            : "bg-slate-100 text-slate-600"
                        }`}
                      >
                        {item.badge}
                      </span>
                    )}
                  </button>
                );
              })}
            </nav>
          </div>

          {/* Sección Inteligencia & Rendimiento */}
          <div>
            <p className="px-3 text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2">
              Inteligencia & Finanzas
            </p>
            <nav className="space-y-1">
              {itemsInteligencia.map((item) => {
                const activo = moduloActivo === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => onCambiarModulo(item.id)}
                    className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl font-medium text-xs transition-all duration-150 ${
                      activo
                        ? "bg-indigo-50 text-indigo-600 shadow-sm border border-indigo-100/80 font-semibold"
                        : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
                    }`}
                  >
                    <div className="flex items-center gap-2.5">
                      <span className="text-base">{item.icono}</span>
                      <span>{item.nombre}</span>
                    </div>
                    {item.badge && (
                      <span
                        className={`text-[10px] px-2 py-0.5 rounded-full font-semibold ${
                          activo
                            ? "bg-indigo-600 text-white"
                            : "bg-indigo-50 text-indigo-500 border border-indigo-100"
                        }`}
                      >
                        {item.badge}
                      </span>
                    )}
                  </button>
                );
              })}
            </nav>
          </div>
        </div>
      </div>

      {/* 3. Footer: Estado del Sistema */}
      <div className="p-4 border-t border-slate-100 bg-slate-50/70">
        <div className="bg-white border border-slate-200/80 rounded-xl p-3 shadow-xs">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-[11px] font-semibold text-slate-700 flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              Agente Dapta
            </span>
            <span className="text-[10px] text-emerald-600 bg-emerald-50 border border-emerald-100 px-1.5 py-0.2 rounded font-medium">
              En línea
            </span>
          </div>
          <p className="text-[11px] text-slate-500">
            {totalCalificados} leads calificados con scoring &gt; 0.60
          </p>
          <div className="mt-2 pt-2 border-t border-slate-100 flex items-center justify-between text-[10px] text-slate-400">
            <span>Tokens LLM RAG</span>
            <span className="font-mono text-slate-600">$0.0003 USD</span>
          </div>
        </div>
      </div>
    </aside>
  );
}
