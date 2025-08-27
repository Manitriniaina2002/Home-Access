from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics import renderPDF
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph

OUT = "presentation_slides.pdf"
WIDTH, HEIGHT = landscape(A4)

# Color palette from base template
COLORS = {
    "primary-500": colors.HexColor("#0ea5e9"),
    "primary-600": colors.HexColor("#0284c7"),
    "primary-700": colors.HexColor("#0369a1"),
    "neutral-50": colors.HexColor("#f8fafc"),
    "neutral-100": colors.HexColor("#f1f5f9"),
    "neutral-900": colors.HexColor("#0f172a"),
    "success-500": colors.HexColor("#10b981"),
    "neutral-600": colors.HexColor("#475569"),
}

# Spacing and typography from base template (converted to cm for ReportLab)
SPACING = {
    "space-2": 0.5 * cm,
    "space-4": 1 * cm,
    "space-6": 1.5 * cm,
    "text-2xl": 24,  # 1.5rem * 16px/rem
    "text-base": 16,  # 1rem * 16px/rem
    "text-sm": 14,    # 0.875rem * 16px/rem
    "radius-md": 0.5 * cm,
}

def draw_header(c, title):
    """Draw a modern header with gradient and shadow."""
    # Gradient header background
    c.saveState()
    c.setFillColor(COLORS["primary-500"])
    c.setStrokeColor(COLORS["primary-700"])
    c.setLineWidth(0.1)
    c.rect(SPACING["space-4"], HEIGHT - 3.5 * cm, WIDTH - 2 * SPACING["space-4"], 2 * cm, fill=1, stroke=1)
    c.setFillColor(COLORS["primary-700"])
    c.rect(SPACING["space-4"], HEIGHT - 3.5 * cm, (WIDTH - 2 * SPACING["space-4"]) / 2, 2 * cm, fill=1, stroke=0)
    
    # Shadow effect
    shadow = Drawing(WIDTH, 0.2 * cm)
    shadow.add(Rect(SPACING["space-4"], 0, WIDTH - 2 * SPACING["space-4"], 0.2 * cm, fillColor=colors.HexColor("#00000020")))
    renderPDF.draw(shadow, c, 0, HEIGHT - 3.7 * cm)
    
    # Title text
    c.setFont("Helvetica-Bold", SPACING["text-2xl"])
    c.setFillColor(colors.white)
    c.drawString(SPACING["space-6"], HEIGHT - 2.5 * cm, title)
    c.restoreState()

def draw_bullets(c, items, start_y):
    """Draw bullet points with modern styling."""
    c.setFont("Helvetica", SPACING["text-base"])
    y = start_y
    for text in items:
        # Bullet as filled circle
        c.setFillColor(COLORS["primary-600"])
        c.circle(SPACING["space-6"] + 0.3 * cm, y - 0.15 * cm, 0.15 * cm, fill=1)
        # Text
        c.setFillColor(COLORS["neutral-900"])
        styles = getSampleStyleSheet()
        style = styles["Normal"]
        style.fontSize = SPACING["text-base"]
        style.leading = SPACING["text-base"] * 1.2
        p = Paragraph(text, style)
        p.wrap(WIDTH - 3 * SPACING["space-6"], 1.2 * cm)
        p.drawOn(c, SPACING["space-6"] + 0.8 * cm, y - 0.3 * cm)
        y -= 1.5 * cm

def draw_footer(c, note, page_num):
    """Draw a modern footer with background and page number."""
    c.saveState()
    # Footer background
    c.setFillColor(COLORS["neutral-50"])
    c.setStrokeColor(COLORS["neutral-100"])
    c.setLineWidth(0.1)
    c.rect(SPACING["space-4"], 0.5 * cm, WIDTH - 2 * SPACING["space-4"], 1.2 * cm, fill=1, stroke=1)
    # Footer text
    c.setFont("Helvetica-Oblique", SPACING["text-sm"])
    c.setFillColor(COLORS["neutral-600"])
    c.drawString(SPACING["space-6"], 0.9 * cm, note)
    # Page number
    c.drawRightString(WIDTH - SPACING["space-6"], 0.9 * cm, f"Page {page_num}")
    c.restoreState()

def draw_background(c):
    """Draw a subtle grid background for modern tech feel."""
    c.saveState()
    c.setStrokeColor(COLORS["neutral-100"])
    c.setLineWidth(0.05)
    # Vertical grid lines
    for x in range(int(SPACING["space-4"]), int(WIDTH - SPACING["space-4"]), int(2 * cm)):
        c.line(x, SPACING["space-4"], x, HEIGHT - SPACING["space-4"])
    # Horizontal grid lines
    for y in range(int(SPACING["space-4"]), int(HEIGHT - SPACING["space-4"]), int(2 * cm)):
        c.line(SPACING["space-4"], y, WIDTH - SPACING["space-4"], y)
    c.restoreState()

def create_slide_1(c, page_num):
    draw_background(c)
    draw_header(c, "Architecture & Flux")
    bullets = [
        "ESP32 → MQTT (broker.hivemq.com): topic home_access/...",
        "Django run_mqtt (paho-mqtt) → persiste DoorEvent en BDD",
        "Signals → Channel layer → Django Channels (Daphne) broadcast",
        "Dashboard JS (WebSocket): mise à jour en temps réel",
    ]
    draw_bullets(c, bullets, HEIGHT - 5 * cm)
    draw_footer(c, "Montrer le flux bout-en-bout: publier MQTT → voir apparaître le log.", page_num)

def create_slide_2(c, page_num):
    draw_background(c)
    draw_header(c, "Démo Live / Commandes")
    bullets = [
        "Activer venv, installer dépendances, appliquer migrations",
        "Démarrer ASGI: daphne -b 0.0.0.0 -p 8000 home_acces.asgi:application",
        "Démarrer listener MQTT: python manage.py run_mqtt",
        "Publier test: publish.single('home_access/door_status', 'open', hostname='broker.hivemq.com')",
    ]
    draw_bullets(c, bullets, HEIGHT - 5 * cm)
    draw_footer(c, "Montrer 2 terminaux: Daphne + run_mqtt, puis publier un message de test.", page_num)

def create_slide_3(c, page_num):
    draw_background(c)
    draw_header(c, "Roadmap Technique")
    bullets = [
        "Court terme: Redis channel layer, sécuriser MQTT (TLS/auth), tests automatisés",
        "Moyen terme: i18n complète, UI améliorée (filtres/pagination), monitoring",
        "Long terme: déploiement (Daphne+systemd / Docker), montée en charge, TLS",
    ]
    draw_bullets(c, bullets, HEIGHT - 5 * cm)
    draw_footer(c, "Prioriser sécurité (TLS/Redis) et tests avant production.", page_num)

def main():
    c = canvas.Canvas(OUT, pagesize=landscape(A4))
    # Slide 1
    create_slide_1(c, 1)
    c.showPage()
    # Slide 2
    create_slide_2(c, 2)
    c.showPage()
    # Slide 3
    create_slide_3(c, 3)
    c.showPage()
    c.save()
    print(f"PDF généré : {OUT}")

if __name__ == "__main__":
    main()