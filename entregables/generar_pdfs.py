"""Build the five reviewable PDF deliverables from repository sources.

Requires Python 3.10+, reportlab and pillow. All assets are local and portable.
Run from any directory: python entregables/generar_pdfs.py
"""
from pathlib import Path
import argparse
import html
import json
import re
from itertools import groupby
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, KeepTogether, Image,
    Table, TableStyle, Preformatted, Flowable,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'entregables/assets'
OUT = ROOT / 'entregables/pdf'
TOKENS = dict(re.findall(r'--rg-([\w-]+):\s*(#[0-9a-fA-F]{6})',
                        (ROOT / 'frontend/src/styles/tokens.css').read_text('utf-8')))
C = {key: colors.HexColor(value) for key, value in TOKENS.items()}
METRICS = json.loads((ROOT / 'ml/resultados/metricas.json').read_text('utf-8'))
SUMMARY = next(row for row in json.loads(
    (ROOT / 'data/processed/resumen_datos.json').read_text('utf-8-sig'))
    if row['estacion'] == 'Miravalle')
BASELINE, MODEL = METRICS['persistencia'], METRICS['modelo']
TEST_DAYS = int(METRICS['dias_prueba'])
ADVERSE_DAYS = int(SUMMARY['dias_promedio24h_mayor_25'])
COVERAGE = float(SUMMARY['pct_pm25_con_dato'])

def comparison(metric):
    return f"{BASELINE[metric]:.1f} % / {MODEL[metric]:.1f} %"

pdfmetrics.registerFont(TTFont('Poppins', str(ASSETS / 'Poppins-Regular.ttf')))
pdfmetrics.registerFont(TTFont('Poppins-SemiBold', str(ASSETS / 'Poppins-SemiBold.ttf')))
pdfmetrics.registerFontFamily('Poppins', normal='Poppins', bold='Poppins-SemiBold',
                            italic='Poppins', boldItalic='Poppins-SemiBold')

STYLES = {
    'body': ParagraphStyle('body', fontName='Poppins', fontSize=9.3, leading=14.2,
                           textColor=C['text'], spaceAfter=8, allowWidows=0, allowOrphans=0),
    'h2': ParagraphStyle('h2', fontName='Poppins-SemiBold', fontSize=15, leading=19,
                         textColor=C['ink'], spaceBefore=15, spaceAfter=8,
                         keepWithNext=True),
    'h3': ParagraphStyle('h3', fontName='Poppins-SemiBold', fontSize=11, leading=15,
                         textColor=C['ink'], spaceBefore=10, spaceAfter=6,
                         keepWithNext=True),
    'small': ParagraphStyle('small', fontName='Poppins', fontSize=7.4, leading=11,
                            textColor=C['muted'], spaceAfter=6, splitLongWords=True),
    'bullet': ParagraphStyle('bullet', fontName='Poppins', fontSize=9.3, leading=14.2,
                             leftIndent=13, firstLineIndent=-10, textColor=C['text'],
                             spaceAfter=6),
    'code': ParagraphStyle('code', fontName='Courier', fontSize=7.1, leading=10,
                           textColor=C['ink'], backColor=C['mist'], borderPadding=9,
                           spaceBefore=5, spaceAfter=10),
}

def clean(text):
    return (text.replace('→', ' / ').replace('−', '-').replace('–', '-')
            .replace('—', '-').replace('\u2011', '-').replace('Ω', 'ohm').replace('₂', '2'))

def inline(text):
    text = html.escape(clean(text))
    text = text.replace('&lt;br/&gt;', '<br/>').replace('&amp;gt;', '&gt;')
    text = text.replace('&lt;b&gt;', '<b>').replace('&lt;/b&gt;', '</b>')
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)',
                  lambda m: '<a href="%s" color="%s">%s</a>' %
                  (html.escape(m[2], quote=True), TOKENS['teal'], m[1])
                  if m[2].startswith('http') else m[1], text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'`([^`]+)`', r'<font name="Poppins-SemiBold">\1</font>', text)
    return text

def p(text, style='body'):
    return Paragraph(inline(text), STYLES[style])

def logo(c, x, y, width=145):
    path = ASSETS / 'hackathon-wordmark.jpg'
    im = ImageReader(str(path))
    iw, ih = im.getSize()
    c.drawImage(im, x, y, width=width, height=width * ih / iw,
                preserveAspectRatio=True, mask='auto')

def footer(c, doc):
    w, h = doc.pagesize
    c.setFillColor(C['muted'])
    c.setFont('Poppins', 7)
    c.drawString(44, 25, 'Respira GDL / Prototipo escolar / 16 nov 2026')
    c.drawRightString(w - 44, 25, str(doc.page))
    if doc.page > 1:
        c.setFont('Poppins-SemiBold', 7)
        c.drawString(44, h - 27, 'RESPIRA GDL')

def fit_image(path, max_w, max_h):
    image = Image(str(path))
    scale = min(max_w / image.imageWidth, max_h / image.imageHeight)
    image.drawWidth, image.drawHeight = image.imageWidth * scale, image.imageHeight * scale
    image.hAlign = 'CENTER'
    return image

def cover(title, subtitle, note, image=None):
    story = [Spacer(1, 30), p('HACKATHON JALISCO INTERNACIONAL 2026', 'small'),
             Spacer(1, 18)]
    title_style = ParagraphStyle('cover', fontName='Poppins-SemiBold', fontSize=31,
                                leading=37, textColor=C['ink'], spaceAfter=16)
    story += [Paragraph(inline(title), title_style), p(subtitle), Spacer(1, 15)]
    if image:
        story += [fit_image(image, A4[0] - 88, 218), Spacer(1, 15)]
    story += [p(note), Spacer(1, 12), p('Sergio, Juan, Carlos y Damaris', 'small'),
              p('Revisión documental: 16 de noviembre de 2026', 'small'),
              Spacer(1, 13), fit_image(ASSETS / 'hackathon-wordmark.jpg', 220, 65),
              PageBreak()]
    return story

class DividerDiagram(Flowable):
    """Editable technical diagram of the actual three-resistor divider."""
    def __init__(self):
        super().__init__()
        self.width, self.height = 480, 116

    def draw(self):
        c = self.canv
        c.setStrokeColor(C['ink'])
        c.setFillColor(C['ink'])
        c.setLineWidth(1)
        c.setFont('Poppins', 9)
        c.drawString(0, 84, 'MQ AO')
        c.line(44, 87, 78, 87)
        c.rect(78, 80, 54, 14)
        c.line(132, 87, 157, 87)
        c.rect(157, 80, 54, 14)
        c.line(211, 87, 380, 87)
        c.circle(273, 87, 2, fill=1)
        c.drawString(388, 84, 'GPIO34')
        c.drawString(84, 102, '1 kohm')
        c.drawString(164, 102, '1 kohm')
        c.line(273, 87, 273, 60)
        c.rect(266, 30, 14, 30)
        c.drawString(290, 41, '1 kohm')
        c.line(273, 30, 273, 14)
        c.drawString(260, 0, 'GND')
        c.drawString(0, 25, '5 V en AO / aproximadamente 1.67 V en GPIO34')

def markdown_story(path):
    lines = path.read_text('utf-8').splitlines()
    result, paragraph, code = [], [], None
    def flush():
        if paragraph:
            result.append(p(' '.join(paragraph)))
            paragraph.clear()
    for line in lines:
        if line.startswith('```'):
            flush()
            if code is None:
                code = []
            else:
                block = '\n'.join(code)
                if 'GPIO34' in block and 'MQ AO' in block:
                    result.append(DividerDiagram())
                else:
                    result.append(Preformatted(clean(block), STYLES['code']))
                code = None
            continue
        if code is not None:
            code.append(line)
            continue
        if line.startswith('# '):
            continue
        if not line.strip():
            flush()
        elif line.startswith('## '):
            flush()
            if (path.name == 'manual-usuario.md' and line[3:] == 'Maestra y familias') or (
                path.parent.name == 'semaforo-mq135' and line[3:].startswith('6. OLED')):
                result.append(PageBreak())
            result.append(p(line[3:], 'h2'))
        elif line.startswith('### '):
            flush()
            result.append(p(line[4:], 'h3'))
        elif re.match(r'^(- |\d+\. )', line):
            flush()
            result.append(p(line if not line.startswith('- ') else '• ' + line[2:], 'bullet'))
        else:
            paragraph.append(line)
    flush()
    grouped = []
    for is_list, items in groupby(result, lambda item: isinstance(item, Paragraph) and item.style.name == 'bullet'):
        items = list(items)
        grouped.extend([KeepTogether(items)] if is_list else items)
    for index in range(len(grouped) - 1, 0, -1):
        previous = grouped[index - 1]
        if isinstance(grouped[index], KeepTogether) and isinstance(previous, Paragraph) and previous.style.name in ('h2', 'h3'):
            grouped[index - 1:index + 1] = [KeepTogether([previous] + grouped[index]._content)]
    return grouped

def build_document(name, title, subtitle, source, note, image=None, appendix=None):
    story = cover(title, subtitle, note, image)
    story += markdown_story(ROOT / source)
    if appendix:
        story += ([PageBreak()] if 'manual' in name else []) + appendix
    document = SimpleDocTemplate(str(OUT / name), pagesize=A4,
        leftMargin=44, rightMargin=44, topMargin=47, bottomMargin=47,
        title=title, author='Equipo Respira GDL', subject=subtitle)
    document.build(story, onFirstPage=footer, onLaterPages=footer)

def text_block(c, text, x, y, width, size=19, color='text', bold=False):
    style = ParagraphStyle('slide', fontName='Poppins-SemiBold' if bold else 'Poppins',
                           fontSize=size, leading=size * 1.34, textColor=C[color])
    obj = Paragraph(inline(text), style)
    _, height = obj.wrap(width, 1000)
    obj.drawOn(c, x, y - height)
    return height

def page_base(c, number, title, dark=False):
    w, h = 960, 540
    c.setFillColor(C['white'])
    c.rect(0, 0, w, h, fill=1, stroke=0)
    c.setFillColor(C['mint'])
    c.rect(0, h - 13, w, 13, fill=1, stroke=0)
    text_block(c, title, 52, 485, 860, 32, 'ink', True)
    c.setFont('Poppins', 9)
    c.setFillColor(C['muted'])
    c.drawString(52, 24, 'Respira GDL / Escuela ficticia / Prototipo de demostración')
    c.drawRightString(908, 24, f'{number:02d} / 08')

def slide_notes(c, text):
    text_block(c, text, 52, 75, 855, 9, 'muted')

def build_pitch():
    c = canvas.Canvas(str(OUT / 'pitch-respira-gdl.pdf'), pagesize=(960, 540))
    c.setTitle('Respira GDL / Pitch de ocho diapositivas')
    c.setAuthor('Equipo Respira GDL')
    page_base(c, 1, 'Respira GDL')
    text_block(c, 'Decisiones escolares\nantes de un día de\naire contaminado'.replace('\n', '<br/>'),
               52, 392, 425, 34, 'ink', True)
    text_block(c, 'Miravalle, Guadalajara<br/>Sergio, Juan, Carlos y Damaris',
               52, 208, 420, 16, 'muted')
    im = ImageReader(str(ASSETS / 'campus-detalle.png'))
    iw, ih = im.getSize()
    c.drawImage(im, 485, 151, width=420, height=420 * ih / iw, preserveAspectRatio=True)
    logo(c, 52, 82, 188)
    slide_notes(c, 'Reto 02 / Salud y Bienestar. El campus y sus ocupantes son simulados. Sin validación médica.')
    c.showPage()

    page_base(c, 2, 'Evidencia local y contexto de salud')
    text_block(c, str(ADVERSE_DAYS), 52, 390, 360, 70, 'ink', True)
    text_block(c, 'días observados con PM2.5 diario<br/>mayor a 25 µg/m³ en Miravalle', 52, 295, 400, 21)
    text_block(c, f'2020-2024 / Cobertura horaria: {COVERAGE:.1f} %', 52, 206, 400, 14, 'muted')
    text_block(c, '13,613', 512, 390, 390, 70, 'ink', True)
    text_block(c, 'casos nuevos de asma registrados<br/>en Jalisco durante 2023', 512, 295, 390, 21)
    text_block(c, 'Todas las edades. No estima asma infantil<br/>en una escuela ni causalidad ambiental.', 512, 206, 390, 14, 'muted')
    slide_notes(c, 'SIMAJ: airejalisco.digital/assets/files/historical/BD_2024.xlsx. IIEG/DGE: ficha de enfermedades 2023, p. 3.\nCinco bases anuales oficiales reprocesadas. Histórico exploratorio con cobertura incompleta, sin medición actual.')
    c.showPage()

    page_base(c, 3, 'El recorrido de una maestra')
    for y, n, title, body in [
        (395, '01', 'Consulta el tablero', 'Revisa origen, fecha y aviso de simulación antes de interpretar el color.'),
        (287, '02', 'Revisa las acciones del grupo', 'El plan escolar orienta la jornada. Prevalece el plan médico individual.'),
        (179, '03', 'Prepara el aviso a familias', 'Preparar un mensaje y comprobar su recepción son pasos distintos.')]:
        text_block(c, n, 52, y, 90, 36, 'teal', True)
        text_block(c, title, 157, y, 720, 23, 'ink', True)
        text_block(c, body, 157, y - 39, 720, 17)
    slide_notes(c, 'La demo usa cuentas y alumnos ficticios. El guardado local en un navegador no comparte un expediente entre usuarios.')
    c.showPage()

    page_base(c, 4, 'El prototipo disponible')
    text_block(c, 'Software', 52, 394, 370, 23, 'ink', True)
    text_block(c, 'React + FastAPI / SQLite.<br/>Campus con seis aulas isométricas.<br/>Escenarios de ventilación y ocupación.<br/>Asignación ilustrativa de filtros.', 52, 349, 405, 19)
    text_block(c, 'Montaje electrónico', 515, 394, 390, 23, 'ink', True)
    text_block(c, 'ESP32 + MQ-135 + LEDs + OLED.<br/>MQ en milivoltios sin calibrar.<br/>Simulación identificada por parpadeo.<br/>Falta de información: SIN DATOS.', 515, 349, 390, 19)
    text_block(c, 'Sin PMS5003 ni filtro montado. No hay una reducción física medida.', 52, 177, 850, 22, 'ink', True)
    slide_notes(c, 'El modelo de aula representa un balance de masa ilustrativo, sin calibración de campo. El MQ-135 no mide PM2.5 ni CO₂.')
    c.showPage()

    page_base(c, 5, 'Pronóstico frente a persistencia')
    text_block(c, 'Error absoluto medio / µg/m³', 52, 405, 500, 20, 'ink', True)
    for y, label, value, color in [(327, 'Persistencia', BASELINE['mae'], 'sage'), (259, 'Modelo', MODEL['mae'], 'teal')]:
        text_block(c, label, 52, y + 4, 190, 18)
        c.setFillColor(C[color])
        c.rect(230, y - 20, value * 27, 27, stroke=0, fill=1)
        text_block(c, f'{value:.2f}', 558, y + 5, 100, 20, 'ink', True)
    text_block(c, f'{TEST_DAYS} días de prueba de 2024', 52, 177, 660, 20, 'ink', True)
    text_block(c, f"Mejora de MAE: {METRICS['mejora_mae_pct']:.1f} %", 52, 139, 600, 16, 'muted')
    for y, label, values in [(382, 'Detección adversa', comparison('dias_amarillo_o_rojo_detectados_pct')),
                              (305, 'Falsas alarmas', comparison('falsas_alarmas_pct')),
                              (228, 'Color correcto', comparison('acierto_semaforo_pct'))]:
        text_block(c, label, 690, y, 220, 15, 'muted')
        text_block(c, values, 690, y - 29, 220, 19, 'ink', True)
    slide_notes(c, 'Orden: persistencia / modelo. Fuente: ml/resultados/metricas.json. Reentrenamiento verificado con limpieza corregida.\nVersiones actuales registradas. El entorno previo no quedó documentado. Menor MAE no demuestra eficacia clínica.')
    c.showPage()

    page_base(c, 6, 'Integración y protección de menores')
    text_block(c, 'Ingeniería', 52, 393, 300, 25, 'ink', True)
    text_block(c, 'Interfaz comprensible, actuador y manejo explícito de desconexión.', 52, 346, 365, 20)
    text_block(c, 'Ciencia de datos', 510, 393, 390, 25, 'ink', True)
    text_block(c, 'Evaluación temporal y comparación con una alternativa sencilla.', 510, 346, 390, 20)
    text_block(c, 'Salud pública', 52, 230, 365, 25, 'ink', True)
    text_block(c, 'Prevención escolar, contexto local y acceso sin teléfono.', 52, 182, 365, 20)
    text_block(c, 'Antes de un piloto', 510, 230, 390, 25, 'ink', True)
    text_block(c, 'Autorización, revisión profesional, consentimiento y acceso seguro.', 510, 182, 390, 20)
    slide_notes(c, 'La demo no recopila datos reales de menores. El acceso por rol es simulado y requiere seguridad de producción antes de uso real.')
    c.showPage()

    page_base(c, 7, 'Un piloto que pueda comprobarse')
    rows = [
        ('01', 'Escuela y responsables', 'Autorización, revisión de salud y reglas de privacidad.'),
        ('02', 'Sensores comparables', 'Cotejar dos sensores PM2.5 y registrar cobertura.'),
        ('03', 'Comparación de exposición', 'Periodos con/sin filtro, dentro/fuera y ocupación registrada.'),
        ('04', 'Uso y comunicación', 'Comprensión del semáforo y avisos efectivamente recibidos.'),
    ]
    for i, (num, title, body) in enumerate(rows):
        y = 402 - i * 78
        text_block(c, num, 52, y, 65, 29, 'teal', True)
        text_block(c, title, 134, y, 750, 21, 'ink', True)
        text_block(c, body, 134, y - 34, 750, 16)
    slide_notes(c, 'Propuesta pendiente. El estimador de presupuesto es ilustrativo, sujeto a cotización, mantenimiento y aclaración de la BOM.')
    c.showPage()

    page_base(c, 8, 'La siguiente colaboración')
    text_block(c, 'Una escuela autorizada.<br/>Revisión profesional de salud.<br/>Dos sensores de partículas.', 52, 394, 800, 31, 'ink', True)
    text_block(c, 'Para ejecutar un piloto de exposición y uso con resultados verificables.', 52, 235, 800, 23)
    text_block(c, 'Entregamos código, fuentes y límites del prototipo.<br/>El equipo debe revisar y explicar el trabajo apoyado por IA.', 52, 150, 800, 17, 'muted')
    slide_notes(c, 'Código y demo: github.com/ceilingofe/RespiraGDL / ceilingofe.github.io/RespiraGDL. Sin diagnóstico o eficacia clínica demostrada.')
    c.save()

def build_poster():
    w, h = A4
    c = canvas.Canvas(str(OUT / 'infografia-respira-gdl.pdf'), pagesize=A4)
    c.setTitle('Respira GDL / Infografía de una página')
    c.setAuthor('Equipo Respira GDL')
    c.setFillColor(C['mint'])
    c.rect(0, h - 167, w, 167, stroke=0, fill=1)
    text_block(c, 'Respira GDL', 35, h - 36, w - 70, 36, 'ink', True)
    text_block(c, 'Prevención escolar frente a la contaminación', 35, h - 91, w - 70, 17, 'ink')
    text_block(c, 'Miravalle, Guadalajara / Escuela ficticia / Reto 02', 35, h - 125, w - 70, 10, 'muted')
    text_block(c, 'Evidencia para decidir', 35, 650, 520, 20, 'ink', True)
    text_block(c, f'<b>{ADVERSE_DAYS} días observados</b> con PM2.5 diario &gt;25 µg/m³ en 2020-2024. Cobertura horaria: {COVERAGE:.1f} %. Histórico exploratorio de Miravalle.', 35, 614, 520, 11)
    text_block(c, '<b>13,613 casos nuevos de asma</b> en Jalisco en 2023, todas las edades. Este dato estatal no estima asma infantil ni causalidad ambiental.', 35, 562, 520, 11)
    im = ImageReader(str(ASSETS / 'campus-detalle.png'))
    iw, ih = im.getSize()
    image_w = 282
    c.drawImage(im, 29, 311, width=image_w, height=image_w * ih / iw, preserveAspectRatio=True)
    text_block(c, 'Una demo comprensible', 326, 487, 233, 17, 'ink', True)
    text_block(c, '1. Revisar origen y fecha.<br/><br/>2. Consultar el grupo y sus acciones.<br/><br/>3. Preparar el aviso a familias.', 326, 444, 233, 11)
    text_block(c, 'Campus, ocupantes y filtro simulados.', 35, 302, 520, 9, 'muted')
    text_block(c, 'Qué demostramos', 35, 270, 255, 17, 'ink', True)
    text_block(c, 'Software escolar y escenarios de aula. Firmware para OLED y LEDs. MQ-135 como voltaje sin calibrar, nunca PM2.5 o CO₂.', 35, 236, 247, 10.4)
    text_block(c, 'Qué falta comprobar', 326, 270, 233, 17, 'ink', True)
    text_block(c, 'Montaje físico, sensores de partículas y filtro. Piloto autorizado, comprensión y recepción de avisos. Validación de salud pendiente.', 326, 236, 233, 10.4)
    text_block(c, f"Pronóstico: MAE {MODEL['mae']:.2f} frente a {BASELINE['mae']:.2f} µg/m³ de persistencia, en {TEST_DAYS} días de 2024. El modelo genera más falsas alarmas. Reentrenamiento verificado con limpieza corregida. Sin validación clínica.", 35, 155, 520, 9.1, 'muted')
    text_block(c, 'Fuentes: SIMAJ 2020-2024 e IIEG/DGE, morbilidad 2023 (p. 3). Trazabilidad: docs/datasets.md y ml/resultados/metricas.json en el repositorio.', 35, 94, 348, 7.1, 'muted')
    logo(c, 419, 66, 138)
    text_block(c, 'ceilingofe.github.io/RespiraGDL / No sustituye avisos oficiales o el plan médico individual.', 35, 39, 530, 7.5, 'muted')
    c.save()

def main():
    global OUT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=OUT)
    args = parser.parse_args()
    OUT = args.output_dir.resolve()
    OUT.mkdir(parents=True, exist_ok=True)
    simulator = [p('Campus escolar: simulación de escenarios', 'h2'),
        fit_image(ASSETS / 'campus-detalle.png', 490, 250),
        p('La vista Escuela 3D representa seis salones ficticios. Selecciona un aula para observar ocupantes, filtro, pantalla OLED y semáforo. Son ilustraciones del escenario, no imágenes de una escuela participante.'),
        p('Prueba un cambio a la vez', 'h3'),
        p('1. Mantén iguales las demás condiciones y cambia la ventilación. Observa cómo entra aire exterior y cómo cambia el escenario interior.'),
        p('2. Cambia ocupación y concentración exterior. Las cifras provienen de un modelo ilustrativo de balance de masa, no de sensores instalados.'),
        p('3. Ajusta inventario de filtros y compara su distribución. La asignación usa ocupación para ponderar la exposición del escenario. No representa una recomendación de compra validada.'),
        p('4. Regresa al escenario inicial para comparar. Ninguna reducción mostrada equivale a una medición de este equipo.'),
        p('La ventilación puede introducir partículas cuando el exterior está contaminado. El simulador no evalúa todas las necesidades del aula, como CO₂, temperatura o seguridad. Su uso es educativo.'),
    ]
    build_document('reporte-cientifico-respira-gdl.pdf', 'Respira GDL',
        'Reporte científico / Prevención escolar y pronóstico de PM2.5',
        'docs/reporte-cientifico.md',
        'Evidencia local, evaluación retrospectiva y un prototipo reproducible. Escuela ficticia. Sin reducción física de PM2.5 o beneficio clínico medidos.',
        ASSETS / 'campus-detalle.png')
    build_document('manual-usuario-respira-gdl.pdf', 'Una guía para usar\nRespira GDL'.replace('\n', '<br/>'),
        'Manual de usuario / Maestras, dirección y familias', 'docs/manual-usuario.md',
        'Recorre la demo, identifica el origen de cada dato y reconoce qué hacer cuando falta información. No introduzcas datos reales de menores.',
        ASSETS / 'evidencia-web.png', appendix=simulator)
    build_document('guia-cableado-respira-gdl.pdf', 'Semáforo de salón',
        'Guía de cableado y puesta en marcha / ESP32 + MQ-135 + OLED',
        'firmware/semaforo-mq135/README.md',
        'Pasos para montar y comprobar el circuito disponible. Trabaja con USB desconectado. Este documento no certifica una prueba física del montaje.',
        appendix=[p('Verificación antes de la demostración', 'h2'),
            p('1. Con el USB desconectado, comprueba GND común, polaridad de LEDs, divisor de AO y alimentación de la OLED a 3.3 V.'),
            p('2. Conecta USB estable. Revisa mensajes a 115200 baudios. Evita mostrar credenciales durante la grabación.'),
            p('3. Ejecuta verde, amarillo y rojo. Comprueba un LED por comando y el rótulo PRUEBA SIMULADA en pantalla.'),
            p('4. Ejecuta vivo. Comprueba la URL en la red local. Si no hay dato vigente, la respuesta esperada es SIN DATOS.'),
            p('5. Documenta lo que ocurrió de verdad: compilación, carga, pantalla, cada LED y desconexión son verificaciones distintas. No presentes una prueba pendiente como realizada.'),
            p('Lista de referencia del montaje. No incluye calibración del MQ o validación ambiental.')])
    build_pitch()
    build_poster()
    for path in sorted(OUT.glob('*.pdf')):
        print(f'{path.name}: {path.stat().st_size:,} bytes')

if __name__ == '__main__':
    main()
