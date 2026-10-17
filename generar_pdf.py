"""
generar_pdf.py — Generador de PDF para la documentación de Motor de Leads
========================================================================
Lee FLUJO_COMPLETO_DEL_SISTEMA.txt y genera un PDF profesional y estructurado
en la carpeta idea/ con estilos legibles, fuentes monoespaciadas para diagramas
y saltos de página limpios.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Preformatted, PageBreak, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas


class NumeradorPaginas(canvas.Canvas):
    """Canvas personalizado para incluir encabezado y pie de página con numeración."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_paginas = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_paginas)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_paginas):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Encabezado (solo a partir de la página 2)
        if self._pageNumber > 1:
            self.drawString(54, 750, "Motor de Leads — Documento Completo de Flujo y Arquitectura")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(54, 744, 558, 744)

        # Pie de página
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 45, 558, 45)
        self.drawString(54, 32, "Hackathon Dapta 2024 · Intent-Based Lead Engine + Unit Economics Tracker")
        pag_texto = f"Página {self._pageNumber} de {total_paginas}"
        self.drawRightString(558, 32, pag_texto)
        self.restoreState()


def generar_pdf_desde_txt(ruta_txt: str, ruta_pdf: str):
    """Convierte el archivo TXT de flujo y arquitectura en un documento PDF estructurado."""
    if not os.path.exists(ruta_txt):
        print(f"Error: {ruta_txt} no existe.")
        return

    doc = SimpleDocTemplate(
        ruta_pdf,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    estilos = getSampleStyleSheet()

    # Estilos tipográficos
    estilo_titulo = ParagraphStyle(
        "TituloPortada",
        parent=estilos["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1e293b"),
        alignment=1, # Centrado
    )

    estilo_subtitulo = ParagraphStyle(
        "SubtituloPortada",
        parent=estilos["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=16,
        textColor=colors.HexColor("#475569"),
        alignment=1,
    )

    estilo_h1 = ParagraphStyle(
        "SeccionH1",
        parent=estilos["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=18,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True,
    )

    estilo_cuerpo = ParagraphStyle(
        "Cuerpo",
        parent=estilos["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155"),
        spaceAfter=4,
    )

    estilo_mono = ParagraphStyle(
        "BloqueMono",
        parent=estilos["Normal"],
        fontName="Courier",
        fontSize=7,
        leading=9.5,
        textColor=colors.HexColor("#0f172a"),
    )

    elementos = []

    with open(ruta_txt, "r", encoding="utf-8") as f:
        lineas = f.readlines()

    # Portada simplificada
    elementos.append(Spacer(1, 20))
    elementos.append(Paragraph("MOTOR DE LEADS", estilo_titulo))
    elementos.append(Spacer(1, 6))
    elementos.append(Paragraph("Intent-Based Lead Engine + Unit Economics Tracker", estilo_subtitulo))
    elementos.append(Paragraph("Documento de Flujo, Arquitectura e Idea Desarrollada — Hackathon Dapta 2024", estilo_subtitulo))
    elementos.append(Spacer(1, 20))

    bloque_mono = []
    en_bloque_mono = False

    for linea in lineas:
        linea_str = linea.rstrip("\r\n")

        # Detectar líneas separadoras principales
        if linea_str.startswith("========"):
            if bloque_mono:
                texto_pre = "\n".join(bloque_mono)
                elementos.append(Preformatted(texto_pre, estilo_mono))
                bloque_mono = []
            continue

        # Detectar títulos de sección numerada (ej. "1. RESUMEN EJECUTIVO", "6. FLUJO END-TO-END...")
        es_titulo_seccion = False
        partes = linea_str.strip().split(".", 1)
        if len(partes) == 2 and partes[0].isdigit() and partes[1].strip().isupper():
            es_titulo_seccion = True

        if es_titulo_seccion:
            if bloque_mono:
                texto_pre = "\n".join(bloque_mono)
                elementos.append(Preformatted(texto_pre, estilo_mono))
                bloque_mono = []
            elementos.append(Spacer(1, 10))
            elementos.append(Paragraph(linea_str.strip(), estilo_h1))
            elementos.append(Spacer(1, 4))
            continue

        # Si la línea contiene arte ASCII o tablas de cajas (|, +, -, ┌, ├, │, └, etc.)
        es_caracter_grafico = any(c in linea_str for c in ["┌", "├", "│", "└", "─", "┼", "→", "↓", "│", "+-", "===", "|", "  •", "  -"])

        if es_caracter_grafico or linea_str.startswith("    ") or (linea_str.startswith("  ") and not linea_str.strip().startswith("•")):
            bloque_mono.append(linea_str)
        else:
            if bloque_mono:
                texto_pre = "\n".join(bloque_mono)
                elementos.append(Preformatted(texto_pre, estilo_mono))
                bloque_mono = []

            if linea_str.strip():
                # Reemplazar caracteres especiales HTML
                texto_limpio = linea_str.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                elementos.append(Paragraph(texto_limpio, estilo_cuerpo))
            else:
                elementos.append(Spacer(1, 4))

    if bloque_mono:
        texto_pre = "\n".join(bloque_mono)
        elementos.append(Preformatted(texto_pre, estilo_mono))

    doc.build(elementos, canvasmaker=NumeradorPaginas)
    print(f"PDF generado exitosamente en: {ruta_pdf}")


if __name__ == "__main__":
    txt_origen = "FLUJO_COMPLETO_DEL_SISTEMA.txt"
    pdf_destino = os.path.join("idea", "FLUJO_COMPLETO_DEL_SISTEMA.pdf")
    generar_pdf_desde_txt(txt_origen, pdf_destino)
