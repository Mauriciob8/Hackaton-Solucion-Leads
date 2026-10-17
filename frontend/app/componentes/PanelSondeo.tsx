/**
 * PanelSondeo.tsx — Lanzador de Detección Activa (Estilo SaaS Moderno)
 * ===================================================================
 * Configura los parámetros del scraper con selectores limpios,
 * presets rápidos y tarjetas de fuentes de datos gratuitas.
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
  { valor: "",              etiqueta: "Todos los sectores" },
  { valor: "restaurante",   etiqueta: "🍽️ Restaurantes y Gastronomía" },
  { valor: "clinica",       etiqueta: "🏥 Clínicas y Centros de Salud" },
  { valor: "taller",        etiqueta: "🔧 Talleres Automotrices" },
  { valor: "salon_belleza", etiqueta: "💅 Salones de Belleza y Spas" },
  { valor: "inmobiliaria",  etiqueta: "🏠 Inmobiliarias y Propiedades" },
  { valor: "comercio",      etiqueta: "🛒 Comercio Minorista" },
  { valor: "distribucion",  etiqueta: "📦 Distribución y Logística" },
];

const CANALES_DISPONIBLES = [
  { valor: "email",          etiqueta: "📧 Email Transaccional (Resend)",     costo: "$0.0002" },
  { valor: "whatsapp",       etiqueta: "💬 WhatsApp Cloud API (Meta)",        costo: "$0.0350" },
  { valor: "formulario_web", etiqueta: "🌐 Formulario Web (Playwright)",      costo: "$0.0000" },
];

export default function PanelSondeo({
  onDetectar,
  detectando,
  ultimaDeteccion,
}: PropsPanelSondeo) {
  const [sector,   setSector]   = useState("");
  const [ciudad,   setCiudad]   = useState("");
  const [canal,    setCanal]    = useState("whatsapp");
  const [cantidad, setCantidad] = useState(10);

  async function handleLanzar() {
    await onDetectar(sector, ciudad, canal, cantidad);
  }

  function aplicarPreset(sectorP: string, ciudadP: string, canalP: string, cantP: number) {
    setSector(sectorP);
    setCiudad(ciudadP);
    setCanal(canalP);
    setCantidad(cantP);
  }

  return (
    <div className="bg-white border border-slate-200/90 rounded-2xl p-6 shadow-xs space-y-6">
      {/* Encabezado con presets */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-slate-100 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-slate-900 font-bold text-base">
              Detección Activa de Oportunidades
            </h2>
            <span className="text-[10px] font-bold bg-indigo-50 text-indigo-700 border border-indigo-100 px-2 py-0.5 rounded-full">
              Intent Scraping
            </span>
          </div>
          <p className="text-slate-500 text-xs mt-0.5">
            Rastreo automatizado de dolor operativo en fuentes públicas de libre acceso
          </p>
        </div>

        {/* Presets rápidos */}
        <div className="flex items-center gap-1.5 flex-wrap">
          <span className="text-[11px] text-slate-400 font-medium">Búsquedas rápidas:</span>
          <button
            onClick={() => aplicarPreset("restaurante", "Bogotá", "whatsapp", 10)}
            className="text-[11px] bg-slate-50 hover:bg-slate-100 text-slate-700 border border-slate-200 px-2 py-1 rounded-md transition-colors"
          >
            🍽️ Restaurantes Bogotá
          </button>
          <button
            onClick={() => aplicarPreset("clinica", "Medellín", "whatsapp", 10)}
            className="text-[11px] bg-slate-50 hover:bg-slate-100 text-slate-700 border border-slate-200 px-2 py-1 rounded-md transition-colors"
          >
            🏥 Clínicas Medellín
          </button>
        </div>
      </div>

      {/* Controles del formulario */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Sector */}
        <div>
          <label className="text-slate-500 text-xs font-semibold block mb-1.5 uppercase tracking-wider">
            Sector Industrial
          </label>
          <select
            value={sector}
            onChange={(e) => setSector(e.target.value)}
            className="w-full bg-slate-50/80 border border-slate-200 text-slate-800 text-xs rounded-xl px-3 py-2.5 focus:outline-none focus:bg-white focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 transition-all font-medium"
          >
            {SECTORES_DISPONIBLES.map((s) => (
              <option key={s.valor} value={s.valor}>{s.etiqueta}</option>
            ))}
          </select>
        </div>

        {/* Ciudad */}
        <div>
          <label className="text-slate-500 text-xs font-semibold block mb-1.5 uppercase tracking-wider">
            Ciudad / Región
          </label>
          <input
            type="text"
            value={ciudad}
            onChange={(e) => setCiudad(e.target.value)}
            placeholder="Ej: Bogotá, Cali, Medellín..."
            className="w-full bg-slate-50/80 border border-slate-200 text-slate-800 text-xs rounded-xl px-3 py-2.5 focus:outline-none focus:bg-white focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 transition-all font-medium placeholder:text-slate-400"
          />
        </div>

        {/* Canal Inicial */}
        <div>
          <label className="text-slate-500 text-xs font-semibold block mb-1.5 uppercase tracking-wider">
            Canal Preferente
          </label>
          <select
            value={canal}
            onChange={(e) => setCanal(e.target.value)}
            className="w-full bg-slate-50/80 border border-slate-200 text-slate-800 text-xs rounded-xl px-3 py-2.5 focus:outline-none focus:bg-white focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 transition-all font-medium"
          >
            {CANALES_DISPONIBLES.map((c) => (
              <option key={c.valor} value={c.valor}>
                {c.etiqueta} ({c.costo})
              </option>
            ))}
          </select>
        </div>

        {/* Límite */}
        <div>
          <label className="text-slate-500 text-xs font-semibold block mb-1.5 uppercase tracking-wider">
            Límite de Prospectos: <span className="text-indigo-600 font-bold">{cantidad}</span>
          </label>
          <input
            type="range"
            min={1}
            max={30}
            value={cantidad}
            onChange={(e) => setCantidad(Number(e.target.value))}
            className="w-full accent-indigo-600 cursor-pointer mt-2"
          />
        </div>
      </div>

      {/* Botón de acción principal */}
      <div className="flex items-center gap-4 pt-2">
        <button
          onClick={handleLanzar}
          disabled={detectando}
          className={`flex items-center gap-2 px-6 py-2.5 rounded-xl font-bold text-xs text-white transition-all shadow-md ${
            detectando
              ? "bg-indigo-400 cursor-not-allowed"
              : "bg-indigo-600 hover:bg-indigo-700 shadow-indigo-600/20 hover:shadow-indigo-600/30"
          }`}
        >
          <span>{detectando ? "⏳" : "⚡"}</span>
          <span>{detectando ? "Extrayendo señales de dolor..." : "Ejecutar Búsqueda de Dolor"}</span>
        </button>

        {ultimaDeteccion && (
          <div className="text-xs text-emerald-700 bg-emerald-50 border border-emerald-200 px-3 py-1.5 rounded-lg flex items-center gap-2">
            <span>✓</span>
            <span>
              <strong>{ultimaDeteccion.cantidad}</strong> leads detectados y guardados
            </span>
            <span className="text-slate-400 text-[10px]">({ultimaDeteccion.timestamp})</span>
          </div>
        )}
      </div>

      {/* 3 Fuentes gratuitas destacadas */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 pt-3 border-t border-slate-100">
        {[
          {
            icono: "🗺️",
            titulo: "Reseñas Google Maps",
            desc: "Quejas por lentitud en responder WhatsApp, pérdida de pedidos o no-shows.",
            tag: "Costo Scraping: $0.0001",
          },
          {
            icono: "💼",
            titulo: "Portales de Empleo",
            desc: "Vacantes para asistentes de ventas o digitadores en Excel que delatan procesos manuales.",
            tag: "Costo Scraping: $0.0001",
          },
          {
            icono: "🌐",
            titulo: "Auditoría Web Automática",
            desc: "Sitios con carga móvil superior a 5s o sin botón de contacto directo a WhatsApp.",
            tag: "Costo Scraping: $0.0001",
          },
        ].map((fuente) => (
          <div
            key={fuente.titulo}
            className="bg-slate-50/70 border border-slate-200/70 rounded-xl p-3.5 flex items-start gap-3 sombra-card-hover"
          >
            <span className="text-2xl p-2 bg-white rounded-lg border border-slate-200/80 shadow-2xs">
              {fuente.icono}
            </span>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between gap-1">
                <p className="text-xs font-bold text-slate-800">{fuente.titulo}</p>
              </div>
              <p className="text-[11px] text-slate-500 mt-1 leading-relaxed">
                {fuente.desc}
              </p>
              <span className="inline-block mt-2 text-[10px] text-indigo-600 font-semibold bg-indigo-50 border border-indigo-100 px-2 py-0.5 rounded-md">
                {fuente.tag}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
