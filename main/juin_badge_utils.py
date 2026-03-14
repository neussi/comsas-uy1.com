"""
juin_badge_utils.py — Génération de badges commission J.U.IN 2026
Style premium, A6 vertical, avec photo circulaire, nom, commission, rôle.
"""
import os
from io import BytesIO
from django.core.files import File
from django.conf import settings
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A6
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth
from PIL import Image, ImageOps, ImageDraw


JUIN_NAVY    = colors.Color(15/255, 23/255, 42/255)   # #0F172A deep navy
JUIN_GOLD    = colors.Color(234/255, 179/255, 8/255)   # #EAB308 gold accent
JUIN_CYAN    = colors.Color(6/255, 182/255, 212/255)   # #06B6D4 cyan
JUIN_WHITE   = colors.white
JUIN_LIGHT   = colors.Color(0.97, 0.97, 0.97)


def _circular_photo(img_path, size=400):
    """Returns a circular PIL RGBA image or None."""
    try:
        if not os.path.exists(img_path):
            return None
        img = Image.open(img_path).convert("RGBA")
        img = ImageOps.fit(img, (size, size), centering=(0.5, 0.5))
        mask = Image.new('L', (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size, size), fill=255)
        out = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        out.paste(img, (0, 0), mask=mask)
        return out
    except Exception as e:
        print(f"[JUIN Badge] Photo error: {e}")
        return None


def generate_juin_commission_badge(application):
    """
    Génère un badge PDF de commission pour un(e) candidat(e) approuvé(e).
    Returns the URL of the generated badge or None.
    """
    buffer = BytesIO()
    width, height = A6
    p = canvas.Canvas(buffer, pagesize=A6)

    # ── Background ──────────────────────────────────────────────────────────
    p.setFillColor(JUIN_WHITE)
    p.rect(0, 0, width, height, fill=1, stroke=0)

    # Subtle watermark text
    p.saveState()
    p.setFillColor(colors.Color(0.95, 0.95, 0.97))
    p.setFont("Helvetica-Bold", 70)
    p.translate(width / 2, height / 2)
    p.rotate(35)
    p.drawCentredString(0, 0, "J.U.IN")
    p.restoreState()

    # ── Header Navy Block ─────────────────────────────────────────────────
    HEADER_H = 55 * mm
    p.setFillColor(JUIN_NAVY)
    hdr = p.beginPath()
    hdr.moveTo(0, height)
    hdr.lineTo(width, height)
    hdr.lineTo(width, height - HEADER_H)
    hdr.curveTo(width * 0.65, height - HEADER_H + 6 * mm,
                width * 0.35, height - HEADER_H - 6 * mm,
                0, height - HEADER_H)
    hdr.close()
    p.drawPath(hdr, fill=1, stroke=0)

    # Gold top-left accent
    p.setFillColor(JUIN_GOLD)
    gold = p.beginPath()
    gold.moveTo(0, height)
    gold.lineTo(28 * mm, height)
    gold.curveTo(14 * mm, height - 14 * mm, 5 * mm, height - 20 * mm, 0, height - 32 * mm)
    gold.close()
    p.drawPath(gold, fill=1, stroke=0)

    # Cyan right accent
    p.setFillColor(JUIN_CYAN)
    base_y = height - HEADER_H
    cy = p.beginPath()
    cy.moveTo(width, base_y + 12 * mm)
    cy.lineTo(width, base_y - 12 * mm)
    cy.curveTo(width - 14 * mm, base_y, width - 22 * mm, base_y + 5 * mm,
               width - 18 * mm, base_y + 12 * mm)
    cy.close()
    p.drawPath(cy, fill=1, stroke=0)

    # ── Logo COMSAS ───────────────────────────────────────────────────────
    LOGO_SIZE = 12 * mm
    logo_path = os.path.join(settings.BASE_DIR, 'static/images/comsas.png')
    if os.path.exists(logo_path):
        p.setFillColor(JUIN_WHITE)
        p.circle(10 * mm + LOGO_SIZE / 2, height - 16 * mm, LOGO_SIZE / 2 + 1.5 * mm, fill=1, stroke=0)
        p.drawImage(ImageReader(logo_path), 10 * mm, height - 22 * mm,
                    width=LOGO_SIZE, height=LOGO_SIZE, mask='auto', preserveAspectRatio=True)

    # Edition badge top-right
    p.setFillColor(JUIN_GOLD)
    p.roundRect(width - 30 * mm, height - 14 * mm, 26 * mm, 9 * mm, 4 * mm, fill=1, stroke=0)
    p.setFillColor(JUIN_NAVY)
    p.setFont("Helvetica-Bold", 8)
    edition = application.commission.edition
    p.drawCentredString(width - 17 * mm, height - 11 * mm, f"{edition.edition_number}e ÉDITION")

    # ── Photo ─────────────────────────────────────────────────────────────
    PHOTO_SIZE = 34 * mm
    px = (width - PHOTO_SIZE) / 2
    py = height - 50 * mm

    # White ring
    p.setLineWidth(3)
    p.setStrokeColor(JUIN_WHITE)
    p.circle(width / 2, py + PHOTO_SIZE / 2, PHOTO_SIZE / 2 + 1.5 * mm, fill=0, stroke=1)
    # Cyan ring
    p.setLineWidth(1.2)
    p.setStrokeColor(JUIN_CYAN)
    p.arc(px - 2 * mm, py - 2 * mm, px + PHOTO_SIZE + 2 * mm, py + PHOTO_SIZE + 2 * mm, 45, 135)
    # Gold ring
    p.setStrokeColor(JUIN_GOLD)
    p.arc(px - 2 * mm, py - 2 * mm, px + PHOTO_SIZE + 2 * mm, py + PHOTO_SIZE + 2 * mm, 225, 315)

    # Draw photo or placeholder
    has_photo = False
    if application.photo:
        img_path = application.photo.path
        circ = _circular_photo(img_path, size=500)
        if circ:
            buf2 = BytesIO()
            circ.save(buf2, 'PNG')
            buf2.seek(0)
            p.drawImage(ImageReader(buf2), px, py, width=PHOTO_SIZE, height=PHOTO_SIZE,
                        mask='auto', preserveAspectRatio=True)
            has_photo = True

    if not has_photo:
        p.setFillColor(colors.Color(0.88, 0.88, 0.92))
        p.circle(width / 2, py + PHOTO_SIZE / 2, PHOTO_SIZE / 2, fill=1, stroke=0)
        p.setFillColor(JUIN_NAVY)
        p.setFont("Helvetica-Bold", 22)
        initials = "".join([w[0].upper() for w in application.nom_prenom.split()[:2]])
        p.drawCentredString(width / 2, py + PHOTO_SIZE / 2 - 4 * mm, initials)

    # ── Body text ────────────────────────────────────────────────────────
    # Commission badge
    commission_text = application.commission.code
    p.setFillColor(JUIN_CYAN)
    badge_w = stringWidth(commission_text, "Helvetica-Bold", 9) + 12 * mm
    badge_x = (width - badge_w) / 2
    badge_y = py - 10 * mm
    p.roundRect(badge_x, badge_y, badge_w, 7 * mm, 3 * mm, fill=1, stroke=0)
    p.setFillColor(JUIN_WHITE)
    p.setFont("Helvetica-Bold", 9)
    p.drawCentredString(width / 2, badge_y + 2 * mm, commission_text)

    # Full name
    name_y = badge_y - 10 * mm
    p.setFillColor(JUIN_NAVY)
    p.setFont("Helvetica-Bold", 18)
    name = application.nom_prenom.upper()
    if stringWidth(name, "Helvetica-Bold", 18) > width - 8 * mm:
        p.setFont("Helvetica-Bold", 14)
    if stringWidth(name, "Helvetica-Bold", 14) > width - 8 * mm:
        p.setFont("Helvetica-Bold", 11)
    p.drawCentredString(width / 2, name_y, name)

    # Role
    role_y = name_y - 9 * mm
    p.setFillColor(JUIN_GOLD)
    p.setFont("Helvetica-Bold", 10)
    p.drawCentredString(width / 2, role_y, application.get_commission_role_display().upper())

    # School / Level
    school_y = role_y - 7 * mm
    p.setFillColor(colors.Color(0.4, 0.4, 0.45))
    p.setFont("Helvetica", 9)
    school_label = application.get_etablissement_display()
    if len(school_label) > 40:
        school_label = school_label[:38] + "…"
    p.drawCentredString(width / 2, school_y, f"{school_label}  |  {application.niveau}")

    # ── Footer ───────────────────────────────────────────────────────────
    p.setFillColor(JUIN_NAVY)
    fp = p.beginPath()
    fp.moveTo(0, 0)
    fp.lineTo(width, 0)
    fp.lineTo(width, 8 * mm)
    fp.curveTo(width / 2, 14 * mm, 0, 6 * mm, 0, 6 * mm)
    fp.close()
    p.drawPath(fp, fill=1, stroke=0)

    # Gold line at very bottom
    p.setStrokeColor(JUIN_GOLD)
    p.setLineWidth(2)
    p.line(0, 0, width, 0)

    # Footer text
    p.setFillColor(JUIN_WHITE)
    p.setFont("Helvetica-Bold", 7)
    p.drawCentredString(width / 2, 2 * mm, f"J.U.IN {edition.edition_number}ème Édition  —  comsas-uy1.com  —  \"Coder • Innover • Entreprendre\"")

    # ── Save ─────────────────────────────────────────────────────────────
    p.showPage()
    p.save()
    buffer.seek(0)

    filename = f'juin_badge_{application.pk}.pdf'
    # Store on the application object (we'll add a field for this)
    # For now save to media/juin/badges/
    from django.core.files.storage import default_storage
    path = f'juin/badges/{filename}'
    default_storage.save(path, buffer)
    url = default_storage.url(path)
    return url


def get_juin_badge_path(application):
    """Returns the local filesystem path of the badge if it exists."""
    from django.core.files.storage import default_storage
    path = f'juin/badges/juin_badge_{application.pk}.pdf'
    if default_storage.exists(path):
        return default_storage.path(path)
    return None
