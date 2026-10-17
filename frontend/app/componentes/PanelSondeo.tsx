/**
 * PanelSondeo.tsx — Panel para lanzar detecciones y ver campañas
 * ==============================================================
 * Permite al usuario:
 *  1. Configurar los parámetros del scraper (sector, ciudad, canal)
 *  2. Lanzar la detección de nuevos leads
 *  3. Ver feedback inmediato de los leads detectados
 */

"use client";

import { useState } from "react";

interface PropsPanelSondeo {
  onDetectar: (sector: string, ciudad: string, canal: string, cantidad: number) => Promise<void>;
  detectando?: boolean;
  ultimaDeteccion?: {
    cantidad:  number;
    timestamp: string;
  } | null;
}

const SECTORES_DISPONIBLES = [
  { valor: "",             etiqueta: "Todos los sectores" },
  { valor: "restaurante",  etiqueta: "🍽️ Restaurantes" },
  { valor: "clinica",      etiqueta: "🏥 Clínicas / Salud" },
  { valor: "taller",       etiqueta: "🔧 Talleres Automotrices" },
  { valor: "salon_belleza",etiqueta: "💅 Salones de Belleza" },
  { valor: "inmobiliaria", etiqueta: "🏠 Inmobiliarias" },
  { valor: "comercio",     etiqueta: "🛒 Comercio General" },
  { valor: "distribucion", etiqueta: "📦 Distribución" },
  { valor: "veterinaria",  etiqueta: "🐾 Veterinarias" },
];

const CANALES_DISPONIBLES = [
  { valor: "email",          etiqueta: "📧 Email Transaccional" },
  { valor: "whatsapp",       etiqueta: "💬 WhatsApp Cloud API" },
  { valor: "formulario_web", etiqueta: "🌐 Formulario Web" },
];

export default function PanelSondeo({
  onDetectar,
  detectando,
  ultimaDeteccion,
}: PropsPanelSondeo) {
  const [sector,   setSector]   = useState("");
  const [ciudad,   setCiudad]   = useState("");
  const [canal,    setCanal]    = useState("email");
  const [cantidad, setCantidad] = useState(10);

  async function handleLanzar() {
    await onDetectar(sector, ciudad, canal, cantidad);
  }

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
      {/* Encabezado */}
      <div className="mb-5">
        <h2 className="text-slate-100 font-semibold text-base">
          🔍 Detectar Nuevos Leads
        </h2>
        <p className="text-slate-400 text-xs mt-0.5">
          El scraper buscará pymes con señales de dolor reales en Google Maps,
          portales de empleo y auditorías web.
        </p>
      </div>

      {/* Formulario de parámetros */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-5">
        {/* Sector */}
        <div>
          <label className="text-slate-400 text-xs font-medium block mb-1.5 uppercase tracking-wide">
            Sector objetivo
          </label>
          <select
            value={sector}
            onChange={e => setSector(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 text-slate-100 text-sm rounded-lg px-3 py-2.5 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/30"
          >
            {SECTORES_DISPONIBLES.map(s => (
              <option key={s.valor} value={s.valor}>{s.etiqueta}</option>
            ))}
          </select>
        </div>

        {/* Ciudad */}
        <div>
          <label className="text-slate-400 text-xs font-medium block mb-1.5 uppercase tracking-wide">
            Ciudad (opcional)
          </label>
          <input
            type="text"
            value={ciudad}
            onChange={e => setCiudad(e.target.value)}
            placeholder="Ej: Bogotá, Medellín…"
            className="w-full bg-slate-800 border border-slate-700 text-slate-100 text-sm rounded-lg px-3 py-2.5 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/30 placeholder:text-slate-600"
          />
        </div>

        {/* Canal */}
        <div>
          <label className="text-slate-400 text-xs font-medium block mb-1.5 uppercase tracking-wide">
            Canal de contacto
          </label>
          <select
            value={canal}
            onChange={e => setCanal(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 text-slate-100 text-sm rounded-lg px-3 py-2.5 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/30"
          >
            {CANALES_DISPONIBLES.map(c => (
              <option key={c.valor} value={c.valor}>{c.etiqueta}</option>
            ))}
          </select>
        </div>

        {/* Cantidad */}
        <div>
          <label className="text-slate-400 text-xs font-medium block mb-1.5 uppercase tracking-wide">
            Cantidad máxima
          </label>
          <input
            type="number"
            value={cantidad}
            min={1}
            max={50}
            onChange={e => setCantidad(Number(e.target.value))}
            className="w-full bg-slate-800 border border-slate-700 text-slate-100 text-sm rounded-lg px-3 py-2.5 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/30"
          />
        </div>
      </div>

      {/* Botón de lanzar */}
      <div className="flex items-center gap-4">
        <button
          onClick={handleLanzar}
          disabled={detectando}
          className={`
            px-6 py-2.5 rounded-lg font-medium text-sm transition-all duration-200
            ${detectando
              ? "bg-indigo-600/50 text-indigo-300 cursor-not-allowed"
              : "bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-500/20 hover:shadow-indigo-500/30"
            }
          `}
        >
          {detectando ? "⏳ Detectando leads…" : "🚀 Lanzar Detección"}
        </button>

        {/* Feedback de última detección */}
        {ultimaDeteccion && (
          <div className="text-sm text-emerald-400 flex items-center gap-2">
            <span className="text-emerald-500">✓</span>
            <span>
              <strong>{ultimaDeteccion.cantidad}</strong> leads detectados
            </span>
            <span className="text-slate-600 text-xs">{ultimaDeteccion.timestamp}</span>
          </div>
        )}
      </div>

      {/* Info de fuentes gratuitas */}
      <div className="mt-5 grid grid-cols-1 sm:grid-cols-3 gap-3">
        {[
          {
            icono: "🗺️",
            titulo: "Google Maps",
            desc: "Reseñas con quejas de atención lenta o sin respuesta",
          },
          {
            icono: "💼",
            titulo: "Portales de Empleo",
            desc: "Empresas buscando vendedores junior o personal de atención",
          },
          {
            icono: "🔬",
            titulo: "Auditoría Web",
            desc: "Sitios sin botón WhatsApp o con carga lenta en móvil",
          },
        ].map(fuente => (
          <div
            key={fuente.titulo}
            className="bg-slate-800/40 border border-slate-700/50 rounded-lg p-3 flex gap-3 items-start"
          >
            <span className="text-xl flex-shrink-0">{fuente.icono}</span>
            <div>
              <p className="text-slate-300 text-xs font-semibold">{fuente.titulo}</p>
              <p className="text-slate-500 text-xs mt-0.5">{fuente.desc}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
