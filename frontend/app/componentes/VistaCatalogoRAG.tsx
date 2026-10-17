/**
 * VistaCatalogoRAG.tsx — Explorador interactivo del Catálogo Dapta
 * =================================================================
 * Presenta las 6 soluciones de IA del catálogo oficial indexadas
 * para el Hackathon, con dolores resueltos, casos reales y precios.
 */

"use client";

interface SolucionDapta {
  id: string;
  titulo: string;
  categoria: string;
  sectores_aplicables: string[];
  dolor_objetivo: string;
  descripcion: string;
  resultado_tipico: string;
  caso_exito: string;
  precio_referencial_usd: number;
  tiempo_implementacion_dias: number;
}

const CATALOGO_ESTATICO: SolucionDapta[] = [
  {
    id: "sol-001",
    titulo: "Agente de Atención 24/7 para WhatsApp",
    categoria: "atencion_cliente",
    sectores_aplicables: ["restaurante", "clinica", "taller", "salon_belleza", "tienda"],
    dolor_objetivo: "clientes que no confirman o responden fuera de horario",
    descripcion: "Un agente conversacional en WhatsApp que responde consultas, confirma reservas y da seguimiento automático fuera del horario de atención. Reduce el 80% de los no-shows.",
    resultado_tipico: "Reducción del 80% en no-shows y aumento del 35% en reservas confirmadas",
    caso_exito: "Clínica Dental Medina (Bogotá): pasó de 12 a 2 no-shows semanales en 30 días",
    precio_referencial_usd: 89,
    tiempo_implementacion_dias: 3
  },
  {
    id: "sol-002",
    titulo: "Bot de Respuesta a Reseñas de Google",
    categoria: "reputacion_online",
    sectores_aplicables: ["restaurante", "hotel", "clinica", "taller", "comercio"],
    dolor_objetivo: "reseñas negativas sin respuesta o respuestas lentas",
    descripcion: "Monitorea y responde automáticamente reseñas de Google Maps con tono empático y profesional. Escala reclamos a humanos en menos de 5 minutos.",
    resultado_tipico: "Rating de Google subió de 3.8 a 4.5 en 60 días",
    caso_exito: "Restaurante La Leña (Medellín): recuperó 4 clientes perdidos en el primer mes",
    precio_referencial_usd: 49,
    tiempo_implementacion_dias: 1
  },
  {
    id: "sol-003",
    titulo: "Agente de Seguimiento de Ventas",
    categoria: "ventas_automatizadas",
    sectores_aplicables: ["inmobiliaria", "agencia", "consultora", "tecnologia", "manufactura"],
    dolor_objetivo: "prospectos sin seguimiento por falta de vendedores",
    descripcion: "Agente IA que hace seguimiento recurrente a prospectos vía WhatsApp y Email, califica interés y agenda visitas en el calendario del asesor.",
    resultado_tipico: "3x más citas agendadas sin contratar personal adicional",
    caso_exito: "Inmobiliaria CasaFácil: pasó de 10 a 32 visitas semanales en 45 días",
    precio_referencial_usd: 129,
    tiempo_implementacion_dias: 5
  },
  {
    id: "sol-004",
    titulo: "Asistente de Pedidos por WhatsApp",
    categoria: "operaciones",
    sectores_aplicables: ["restaurante", "tienda", "distribuidora", "panaderia", "farmacia"],
    dolor_objetivo: "pedidos por chat que se traspapelan o tardan en procesarse",
    descripcion: "Recibe y estructura pedidos directamente por WhatsApp, los envía a cocina/bodega al instante y notifica al comprador con tiempos estimados.",
    resultado_tipico: "Eliminación del 95% de pedidos extraviados y 40% menos errores",
    caso_exito: "Panadería El Trigal: procesa 200+ pedidos diarios sin errores",
    precio_referencial_usd: 69,
    tiempo_implementacion_dias: 2
  },
  {
    id: "sol-005",
    titulo: "Auditoría Web Gratuita + Optimización",
    categoria: "presencia_digital",
    sectores_aplicables: ["cualquier_sector"],
    dolor_objetivo: "sitio web lento o sin canal de chat directo",
    descripcion: "Evaluación técnica de velocidad de carga móvil, presencia de botón WhatsApp y SEO local. Se ofrece como gancho no invasivo para pymes.",
    resultado_tipico: "Identificación de 3-5 mejoras que aumentan la conversión un 25%",
    caso_exito: "Taller Automotriz Pérez: instalación del chat en 1 día generó 8 clientes",
    precio_referencial_usd: 0,
    tiempo_implementacion_dias: 0
  },
  {
    id: "sol-006",
    titulo: "Agente de Screening y Selección Inicial",
    categoria: "recursos_humanos",
    sectores_aplicables: ["cualquier_sector"],
    dolor_objetivo: "procesos lentos de filtrado por exceso de postulaciones",
    descripcion: "Agente que recibe candidatos de convocatorias laborales en portales de empleo, realiza preguntas de descarte y clasifica CVs automáticamente.",
    resultado_tipico: "Reducción del 70% en tiempo de revisión y filtrado de candidatos",
    caso_exito: "Cadena MegaShop: contrató 15 cajeros en 5 días en vez de 3 semanas",
    precio_referencial_usd: 99,
    tiempo_implementacion_dias: 3
  }
];

export default function VistaCatalogoRAG() {
  return (
    <div className="space-y-6">
      {/* Encabezado */}
      <div className="bg-white border border-slate-200/90 rounded-2xl p-6 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-slate-900 font-bold text-lg">
              Base de Conocimiento RAG (Catálogo Dapta)
            </h2>
            <span className="text-xs font-semibold bg-indigo-50 text-indigo-700 border border-indigo-100 px-2.5 py-0.5 rounded-full">
              6 Soluciones Indexadas
            </span>
          </div>
          <p className="text-slate-500 text-xs mt-1 max-w-2xl">
            Cada vez que un prospecto responde un micro-sondeo, el motor RAG ejecuta matching contextual
            sobre esta base de soluciones para recomendar la opción exacta respaldada por casos de éxito reales.
          </p>
        </div>
        <div className="text-right">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">Fuente</span>
          <span className="text-xs font-mono font-semibold text-slate-700 bg-slate-50 border border-slate-200 px-2 py-1 rounded">
            catalogo_dapta.json
          </span>
        </div>
      </div>

      {/* Grid de Soluciones */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {CATALOGO_ESTATICO.map((sol) => (
          <div
            key={sol.id}
            className="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-xs sombra-card-hover flex flex-col justify-between"
          >
            <div>
              {/* Header de la card */}
              <div className="flex items-start justify-between gap-2 mb-3">
                <span className="text-xs font-mono font-bold bg-indigo-50 text-indigo-700 border border-indigo-100 px-2 py-0.5 rounded-md">
                  {sol.id}
                </span>
                <span className="text-[11px] font-semibold text-slate-500 capitalize bg-slate-100 px-2 py-0.5 rounded-full">
                  {sol.categoria.replace(/_/g, " ")}
                </span>
              </div>

              <h3 className="font-extrabold text-slate-900 text-sm leading-snug">
                {sol.titulo}
              </h3>

              <p className="text-slate-500 text-xs mt-2 leading-relaxed">
                {sol.descripcion}
              </p>

              {/* Dolor objetivo */}
              <div className="mt-4 p-2.5 bg-slate-50 rounded-xl border border-slate-100">
                <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                  Dolor que Resuelve:
                </p>
                <p className="text-xs text-slate-700 font-medium mt-0.5">
                  &ldquo;{sol.dolor_objetivo}&rdquo;
                </p>
              </div>

              {/* Caso de éxito */}
              <div className="mt-3 p-2.5 bg-emerald-50/50 rounded-xl border border-emerald-100">
                <p className="text-[10px] font-bold text-emerald-800 uppercase tracking-wider">
                  Caso Real Demostrado:
                </p>
                <p className="text-xs text-emerald-950 font-medium mt-0.5">
                  {sol.caso_exito}
                </p>
              </div>
            </div>

            {/* Footer con precio e implementación */}
            <div className="mt-5 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
              <div>
                <span className="text-[10px] text-slate-400 block font-medium">Inversión Base</span>
                <span className="font-extrabold text-slate-900">
                  {sol.precio_referencial_usd === 0 ? "Prueba Gratuita" : `$${sol.precio_referencial_usd} USD/mes`}
                </span>
              </div>
              <div className="text-right">
                <span className="text-[10px] text-slate-400 block font-medium">Implementación</span>
                <span className="font-bold text-indigo-600">
                  {sol.tiempo_implementacion_dias === 0 ? "Inmediata" : `${sol.tiempo_implementacion_dias} días`}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
