"""
generar_pdf_flujo.py — Generador de PDF oficial de alta calidad con ReportLab
Transforma FLUJO_COMPLETO_DEL_SISTEMA.txt en un PDF profesional con paginación,
encabezados, estilos diferenciados y soporte UTF-8 completo.
"""

import os
import shutil
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Preformatted,
    Spacer,
    HRFlowable,
    KeepTogether,
)
from reportlab.pdfgen import canvas


from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

# Registrar fuentes TrueType para soporte UTF-8 nativo en español
pdfmetrics.registerFont(TTFont("Arial", "C:/Windows/Fonts/arial.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Bold", "C:/Windows/Fonts/arialbd.ttf"))
pdfmetrics.registerFont(TTFont("Consolas", "C:/Windows/Fonts/consola.ttf"))


class NumeracionCanvas(canvas.Canvas):
    """Canvas de dos pasadas para calcular e imprimir 'Página X de Y' con encabezado."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.paginas = []

    def showPage(self):
        self.paginas.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total_paginas = len(self.paginas)
        for estado in self.paginas:
            self.__dict__.update(estado)
            self.dibujar_encabezado_y_pie(total_paginas)
            super().showPage()
        super().save()

    def dibujar_encabezado_y_pie(self, total_paginas):
        self.saveState()
        ancho, alto = letter

        # Encabezado
        self.setFont("Arial-Bold", 8)
        self.setFillColor(colors.HexColor("#334155"))
        self.drawString(45, alto - 32, "MOTOR DE LEADS — Intent-Based Lead Engine")
        self.setFont("Arial", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        self.drawRightString(ancho - 45, alto - 32, "Hackathon Dapta 2024 — Versión 2.0")

        # Línea de encabezado
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.6)
        self.line(45, alto - 36, ancho - 45, alto - 36)

        # Línea de pie de página
        self.line(45, 42, ancho - 45, 42)

        # Pie de página
        self.setFont("Arial", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        self.drawString(45, 30, "Documento Completo de Flujo, Arquitectura y Unit Economics")
        self.drawRightString(ancho - 45, 30, f"Página {self._pageNumber} de {total_paginas}")

        self.restoreState()


def generar_pdf(txt_path: str, pdf_output_path: str):
    print(f"[PDF] Leyendo archivo origen: {txt_path}...")
    with open(txt_path, "r", encoding="utf-8", errors="replace") as f:
        contenido = f.read()

    lineas = contenido.splitlines()

    doc = SimpleDocTemplate(
        pdf_output_path,
        pagesize=letter,
        leftMargin=45,
        rightMargin=45,
        topMargin=48,
        bottomMargin=52,
    )

    hoja_estilos = getSampleStyleSheet()

    estilo_titulo = ParagraphStyle(
        "DocTitle",
        parent=hoja_estilos["Heading1"],
        fontName="Arial-Bold",
        fontSize=15,
        leading=19,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=3,
    )

    estilo_subtitulo_doc = ParagraphStyle(
        "DocSubtitle",
        parent=hoja_estilos["Normal"],
        fontName="Arial-Bold",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#475569"),
        spaceAfter=12,
    )

    estilo_seccion = ParagraphStyle(
        "DocHeading1",
        parent=hoja_estilos["Heading1"],
        fontName="Arial-Bold",
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True,
    )

    estilo_subseccion = ParagraphStyle(
        "DocHeading2",
        parent=hoja_estilos["Heading2"],
        fontName="Arial-Bold",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#1e3a8a"),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True,
    )

    estilo_parrafo = ParagraphStyle(
        "DocBody",
        parent=hoja_estilos["Normal"],
        fontName="Arial",
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=4,
    )

    estilo_codigo = ParagraphStyle(
        "DocCode",
        parent=hoja_estilos["Code"],
        fontName="Consolas",
        fontSize=7.2,
        leading=9.0,
        textColor=colors.HexColor("#0f172a"),
        backColor=colors.HexColor("#f8fafc"),
        borderColor=colors.HexColor("#e2e8f0"),
        borderWidth=0.5,
        borderPadding=4,
        spaceBefore=4,
        spaceAfter=6,
    )

    historia = []

    buffer_codigo = []
    en_bloque_codigo = False

    def procesar_buffer_codigo():
        if buffer_codigo:
            texto_bloque = "\n".join(buffer_codigo)
            historia.append(Preformatted(texto_bloque, estilo_codigo))
            buffer_codigo.clear()

    for num_linea, linea in enumerate(lineas):
        linea_strip = linea.strip()

        # Inicio o fin de bloques con ```
        if linea_strip.startswith("```"):
            if en_bloque_codigo:
                procesar_buffer_codigo()
                en_bloque_codigo = False
            else:
                en_bloque_codigo = True
            continue

        if en_bloque_codigo:
            buffer_codigo.append(linea)
            continue

        # Separadores de sección mayores
        if linea_strip == "=" * len(linea_strip) and len(linea_strip) >= 40:
            procesar_buffer_codigo()
            historia.append(Spacer(1, 4))
            historia.append(HRFlowable(width="100%", thickness=1.2, color=colors.HexColor("#2563eb"), spaceAfter=8))
            continue

        # Separadores de subsección menores
        if linea_strip == "─" * len(linea_strip) and len(linea_strip) >= 40:
            procesar_buffer_codigo()
            historia.append(Spacer(1, 2))
            historia.append(HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#94a3b8"), spaceAfter=6))
            continue

        if not linea_strip:
            if buffer_codigo:
                buffer_codigo.append("")
            else:
                historia.append(Spacer(1, 4))
            continue

        # Detección de tablas ASCII o diagramas
        if any(c in linea for c in "┌│└├┼") or (linea.startswith("    •") and ":" in linea):
            buffer_codigo.append(linea)
            continue
        else:
            procesar_buffer_codigo()

        # Detección de encabezados principales (e.g. 1. RESUMEN EJECUTIVO)
        es_encabezado_principal = (
            any(linea_strip.startswith(f"{i}. ") for i in range(1, 25))
            and not linea_strip.startswith("1. BASE")
            and not linea_strip.startswith("1. FATIGA")
            and not linea_strip.startswith("1. Fragmento")
        ) or linea_strip == "ÍNDICE"

        es_subtitulo = (
            linea_strip.startswith("PASO ")
            or linea_strip.startswith("FUENTE ")
            or linea_strip.startswith("1. BASE BENCHMARK")
            or linea_strip.startswith("2. DATOS DEMO")
            or linea_strip.startswith("A. Google Maps")
            or linea_strip.startswith("B. Portales de Empleo")
            or linea_strip.startswith("C. Auditoría Web")
            or linea_strip.startswith("MATRIZ RESUMEN")
            or linea_strip.startswith("ESQUEMA DDL")
            or linea_strip.startswith("DIAGRAMA ENTIDAD")
            or linea_strip.startswith("SISTEMA Y SALUD")
            or linea_strip.startswith("PIPELINE DE LEADS")
            or linea_strip.startswith("MÉTRICAS Y UNIT ECONOMICS")
            or linea_strip.startswith("GESTIÓN DE CAMPAÑAS")
        )

        # Escapar caracteres HTML para Paragraph
        linea_escapada = (
            linea_strip
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

        if linea_strip.startswith("MOTOR DE LEADS —"):
            historia.append(Paragraph(linea_escapada, estilo_titulo))
        elif "Intent-Based Lead Engine" in linea_strip:
            historia.append(Paragraph(linea_escapada, estilo_subtitulo_doc))
        elif es_encabezado_principal:
            historia.append(Paragraph(linea_escapada, estilo_seccion))
        elif es_subtitulo:
            historia.append(Paragraph(linea_escapada, estilo_subseccion))
        else:
            historia.append(Paragraph(linea_escapada, estilo_parrafo))

    procesar_buffer_codigo()

    print("[PDF] Construyendo documento PDF con ReportLab...")
    doc.build(historia, canvasmaker=NumeracionCanvas)
    print(f"[PDF] Generación completada con éxito en: {pdf_output_path}")


if __name__ == "__main__":
    raiz_proyecto = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    txt_origen = os.path.join(raiz_proyecto, "FLUJO_COMPLETO_DEL_SISTEMA.txt")
    pdf_raiz = os.path.join(raiz_proyecto, "FLUJO_COMPLETO_DEL_SISTEMA.pdf")
    pdf_idea = os.path.join(raiz_proyecto, "idea", "FLUJO_COMPLETO_DEL_SISTEMA.pdf")

    generar_pdf(txt_origen, pdf_raiz)

    # Copiar a carpeta idea/
    shutil.copy2(pdf_raiz, pdf_idea)
    print(f"[PDF] Archivo sincronizado con: {pdf_idea}")
