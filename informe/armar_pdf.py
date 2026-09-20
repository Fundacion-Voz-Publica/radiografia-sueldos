from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image,
    PageBreak, HRFlowable, KeepTogether,
)
from reportlab.platypus.flowables import Flowable

AZUL = colors.HexColor("#2a78d6")
AZUL_OSC = colors.HexColor("#184f95")
TINTA = colors.HexColor("#0b0b0b")
TINTA2 = colors.HexColor("#52514e")
MUTED = colors.HexColor("#898781")
SURF2 = colors.HexColor("#f2f1ec")
BORDE = colors.HexColor("#e1e0d9")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle("Eyebrow", fontName="Helvetica-Bold", fontSize=9,
                           textColor=AZUL, leading=11, spaceAfter=4, tracking=0.5))
styles.add(ParagraphStyle("TituloPortada", fontName="Helvetica-Bold", fontSize=28,
                           textColor=TINTA, leading=32, spaceAfter=6))
styles.add(ParagraphStyle("SubtituloPortada", fontName="Helvetica", fontSize=15,
                           textColor=TINTA2, leading=20, spaceAfter=14))
styles.add(ParagraphStyle("H1", fontName="Helvetica-Bold", fontSize=16,
                           textColor=TINTA, leading=20, spaceBefore=4, spaceAfter=10))
styles.add(ParagraphStyle("H2", fontName="Helvetica-Bold", fontSize=11.5,
                           textColor=TINTA, leading=15, spaceBefore=2, spaceAfter=6))
styles.add(ParagraphStyle("Cuerpo", fontName="Helvetica", fontSize=9.7,
                           textColor=TINTA2, leading=14.5, spaceAfter=8))
styles.add(ParagraphStyle("CuerpoChico", fontName="Helvetica", fontSize=8.3,
                           textColor=TINTA2, leading=12.5, spaceAfter=6))
styles.add(ParagraphStyle("BulletCustom", fontName="Helvetica", fontSize=9.7,
                           textColor=TINTA2, leading=14.5, spaceAfter=7, leftIndent=12,
                           bulletIndent=0))
styles.add(ParagraphStyle("KpiLabel", fontName="Helvetica-Bold", fontSize=7.6,
                           textColor=MUTED, leading=10))
styles.add(ParagraphStyle("KpiValue", fontName="Helvetica-Bold", fontSize=16,
                           textColor=TINTA, leading=19, spaceBefore=2))
styles.add(ParagraphStyle("KpiSub", fontName="Helvetica", fontSize=7.8,
                           textColor=TINTA2, leading=10.5, spaceBefore=1))
styles.add(ParagraphStyle("Fuente", fontName="Helvetica", fontSize=8, textColor=MUTED, leading=11))


def fnum(n):
    return f"{round(n):,}".replace(",", ".")


def fmt_clp(v):
    return "$" + fnum(v)


def fmt_miles_millones(v):
    s = f"{v/1e9:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"${s} mil M"


class Regla(Flowable):
    def __init__(self, width, color=BORDE, thickness=0.6):
        super().__init__()
        self.width = width
        self.color = color
        self.thickness = thickness

    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, 0, self.width, 0)


def kpi_table(items, col_width):
    """items: lista de (label, valor, sub)"""
    cells = []
    for label, valor, sub in items:
        cell = [
            Paragraph(label.upper(), styles["KpiLabel"]),
            Paragraph(valor, styles["KpiValue"]),
            Paragraph(sub, styles["KpiSub"]),
        ]
        cells.append(cell)
    t = Table([cells], colWidths=[col_width]*len(items))
    t.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("BOX", (0,0), (-1,-1), 0.6, BORDE),
        ("INNERGRID", (0,0), (-1,-1), 0.6, BORDE),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("RIGHTPADDING", (0,0), (-1,-1), 10),
        ("TOPPADDING", (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ("BACKGROUND", (0,0), (-1,-1), colors.white),
    ]))
    return t


def header_footer(canvas, doc, mes, anio):
    canvas.saveState()
    canvas.setFont("Helvetica", 7.6)
    canvas.setFillColor(MUTED)
    canvas.drawString(20*mm, 12*mm, f"Radiografía de Sueldos del Estado — Informe {mes} {anio} — Fundación Voz Pública")
    canvas.drawRightString(190*mm, 12*mm, f"Página {doc.page}")
    canvas.restoreState()


def construir_pdf(salida, mes, anio, gasto_total, top_gasto, top3, dotacion_total,
                   dot_por_cat, top_dotacion, crecimiento, rangos_eus, grado_mas_bajo,
                   chart_ranking, chart_evolucion, dotacion_serie):
    doc = SimpleDocTemplate(salida, pagesize=LETTER,
                             topMargin=20*mm, bottomMargin=20*mm,
                             leftMargin=20*mm, rightMargin=20*mm,
                             title=f"Radiografía de Sueldos del Estado — {mes} {anio}",
                             author="Fundación Voz Pública")
    W = doc.width
    story = []

    # ---------- Portada ----------
    story.append(Spacer(1, 10*mm))
    story.append(Paragraph("FUNDACIÓN VOZ PÚBLICA", styles["Eyebrow"]))
    story.append(Paragraph("Radiografía de Sueldos del Estado", styles["TituloPortada"]))
    story.append(Paragraph(f"Informe mensual — {mes} de {anio}", styles["SubtituloPortada"]))
    story.append(Regla(W))
    story.append(Spacer(1, 8*mm))
    story.append(Paragraph(
        "Dotación y gasto real en personal del Gobierno Central de Chile, con datos oficiales "
        "de la Dirección de Presupuestos (DIPRES). Este informe resume, mes a mes, cuánta gente "
        "trabaja en el Estado, cuánto cuesta y en qué ministerios se concentra ese gasto.",
        styles["Cuerpo"]))
    story.append(Spacer(1, 10*mm))
    story.append(kpi_table([
        ("Dotación Gobierno Central", fnum(dotacion_total), f"+{crecimiento:.1f}% desde 2016"),
        (f"Gasto real en personal ({mes.lower()})", fmt_miles_millones(gasto_total), "Subtítulo 21, DIPRES"),
        ("Ministerio con más dotación", top_dotacion[0], fnum(top_dotacion[1]+top_dotacion[2]+top_dotacion[3]+top_dotacion[4])+" cargos"),
        ("Ministerio con más gasto", top3[0][0], fmt_miles_millones(top3[0][1])),
    ], W/4))
    story.append(Spacer(1, 14*mm))
    story.append(Paragraph(
        "Elaborado a partir de datos abiertos oficiales — ver fuentes y metodología al final de este informe.",
        styles["Fuente"]))
    story.append(PageBreak())

    # ---------- Resumen ejecutivo ----------
    story.append(Paragraph("Resumen ejecutivo", styles["H1"]))
    dotacion_top_ministerio = top_dotacion[1]+top_dotacion[2]+top_dotacion[3]+top_dotacion[4]
    bullets = [
        (f"El Gobierno Central tiene <b>{fnum(dotacion_total)} cargos</b> en 2025, un "
         f"<b>{crecimiento:.1f}%</b> más que en 2016. La categoría <b>Profesionales</b> concentra la mayor parte "
         f"de esa dotación ({fnum(dot_por_cat['Profesionales'])} personas)."),
        (f"El gasto real en personal (Subtítulo 21) de todo el Gobierno Central en {mes.lower()} de {anio} fue de "
         f"<b>{fmt_miles_millones(gasto_total)}</b>."),
        (f"<b>{top3[0][0]}</b> es el ministerio que más gasta en personal ({fmt_miles_millones(top3[0][1])}), "
         f"seguido de <b>{top3[1][0]}</b> ({fmt_miles_millones(top3[1][1])}) y <b>{top3[2][0]}</b> "
         f"({fmt_miles_millones(top3[2][1])})."),
        (f"<b>{top_dotacion[0]}</b> es el ministerio con más dotación de personal "
         f"({fnum(dotacion_top_ministerio)} cargos)."),
    ]
    for b in bullets:
        story.append(Paragraph("•  " + b, styles["BulletCustom"]))
    story.append(Spacer(1, 6*mm))
    story.append(Paragraph(
        "El detalle interactivo, con desglose por categoría y por institución, está disponible en el "
        "dashboard en línea de Fundación Voz Pública.", styles["CuerpoChico"]))
    story.append(PageBreak())

    # ---------- Gasto por ministerio ----------
    story.append(Paragraph("¿Qué ministerios gastan más en personal?", styles["H1"]))
    story.append(Paragraph(
        f"Gasto real ejecutado en Subtítulo 21 (Gastos en Personal) en {mes.lower()} de {anio}, dato oficial "
        "de DIPRES publicado como datos abiertos — no es una estimación. Se muestran los 15 ministerios "
        "con mayor gasto; la lista completa (31 instituciones) está en el dashboard en línea.",
        styles["Cuerpo"]))
    story.append(Image(chart_ranking, width=W, height=W*4.6/7.2))
    story.append(PageBreak())

    # ---------- Dotación ----------
    story.append(Paragraph("Dotación del Gobierno Central", styles["H1"]))
    story.append(Paragraph(
        "La dotación total del Gobierno Central casi se duplicó en una década. Buena parte del salto "
        "reciente es Educación absorbiendo a los docentes de los Servicios Locales de Educación Pública "
        "(SLEP), antes fuera del Gobierno Central.", styles["Cuerpo"]))
    story.append(Image(chart_evolucion, width=W, height=W*3.4/7.2))
    story.append(Spacer(1, 6*mm))
    story.append(Paragraph("Dotación por categoría (2025)", styles["H2"]))
    tabla_cat = [["Categoría", "Personas", "% del total"]]
    for cat, n in dot_por_cat.items():
        tabla_cat.append([cat, fnum(n), f"{n/dotacion_total*100:.1f}%"])
    t = Table(tabla_cat, colWidths=[W*0.5, W*0.28, W*0.22])
    t.setStyle(_tabla_estilo())
    story.append(t)
    story.append(PageBreak())

    # ---------- Escala de sueldos ----------
    story.append(Paragraph("La escala de sueldos, por categoría", styles["H1"]))
    story.append(Paragraph(
        "La Escala Única de Sueldos (EUS) fija, por ley, la remuneración bruta de cada grado. Estos son los "
        "rangos vigentes en 2025 (escala de la Subsecretaría de Hacienda) para cada categoría de personal.",
        styles["Cuerpo"]))
    tabla_eus = [["Categoría", "Renta bruta mínima", "Renta bruta máxima"]]
    for cat, (lo, hi) in rangos_eus.items():
        tabla_eus.append([cat, fmt_clp(lo), fmt_clp(hi)])
    t2 = Table(tabla_eus, colWidths=[W*0.4, W*0.3, W*0.3])
    t2.setStyle(_tabla_estilo())
    story.append(t2)
    story.append(Spacer(1, 5*mm))
    story.append(Paragraph(
        f"El grado más bajo de toda la escala es el {grado_mas_bajo['grado']} (categoría "
        f"{grado_mas_bajo['cat']}), con una renta bruta de {fmt_clp(grado_mas_bajo['bruta'])}.",
        styles["CuerpoChico"]))
    story.append(PageBreak())

    # ---------- Metodología ----------
    story.append(Paragraph("Fuentes y metodología", styles["H1"]))
    story.append(Paragraph(
        "<b>Dotación:</b> DIPRES, Anuario Estadístico del Empleo Público en el Gobierno Central 2016-2025 "
        "(dipres.gob.cl). Cifras de dotación real por ministerio y categoría, publicadas anualmente.",
        styles["Cuerpo"]))
    story.append(Paragraph(
        "<b>Gasto real en personal:</b> DIPRES, \"Ejecución Presupuestaria del Gobierno Central\", nivel "
        "Partida, vía el Portal de Datos Abiertos del Estado (datos.gob.cl). CSV oficial, publicado "
        "mensualmente, con diccionario de datos incluido.", styles["Cuerpo"]))
    story.append(Paragraph(
        "<b>Escala de sueldos:</b> Subsecretaría de Hacienda, Transparencia Activa, Escala de Remuneraciones "
        "vigente 2025.", styles["Cuerpo"]))
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph(
        "<b>Límites:</b> la dotación de DIPRES es \"Gobierno Central\" — no incluye municipalidades, "
        "universidades estatales, empresas públicas, FF.AA. y de Orden (salvo dotaciones máximas) ni "
        "senadores/diputados. El gasto en personal (Subtítulo 21) incluye personal de planta, a contrata, "
        "honorarios imputados a este ítem, horas extraordinarias y otras asignaciones — no es equivalente "
        "a \"dotación × sueldo\". Es la ejecución de un solo mes, no un promedio anual, así que puede "
        "variar por estacionalidad, bonos o reajustes.", styles["CuerpoChico"]))
    story.append(Spacer(1, 8*mm))
    story.append(Paragraph(
        "Este informe se genera automáticamente cada mes a partir de datos abiertos oficiales, y se "
        "revisa antes de su publicación. Para el detalle interactivo, tramos salariales y una muestra de "
        "las remuneraciones más altas del Estado, visita el dashboard en línea de Fundación Voz Pública.",
        styles["CuerpoChico"]))

    doc.build(story, onFirstPage=lambda c, d: header_footer(c, d, mes, anio),
               onLaterPages=lambda c, d: header_footer(c, d, mes, anio))


def _tabla_estilo():
    return TableStyle([
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("TEXTCOLOR", (0,0), (-1,0), TINTA2),
        ("BACKGROUND", (0,0), (-1,0), SURF2),
        ("TEXTCOLOR", (0,1), (-1,-1), TINTA),
        ("GRID", (0,0), (-1,-1), 0.5, BORDE),
        ("ALIGN", (1,0), (-1,-1), "RIGHT"),
        ("ALIGN", (0,0), (0,-1), "LEFT"),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("RIGHTPADDING", (0,0), (-1,-1), 8),
    ])
