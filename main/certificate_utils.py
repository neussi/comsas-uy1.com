import math
import os
import qrcode
from io import BytesIO
from django.core.files import File
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth
from django.utils import timezone
from django.conf import settings
from django.urls import reverse

# Register decorative calligraphy font if available
FONT_REGISTERED = False
try:
    font_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'GreatVibes-Regular.ttf')
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont('GreatVibes', font_path))
        FONT_REGISTERED = True
except Exception:
    FONT_REGISTERED = False


def render_certificate_pdf(event, participant_data):
    """
    Rendu graphique vectoriel haute-fidélité de l'attestation de prestige.
    Respecte l'esthétique du certificat modèle (angles biseautés bleu/cyan,
    double cadre doré chanfreiné, logo UY1 premier et agrandi, typographie calligraphique,
    sceau d'honneur en or et gestion bi-signataire en présentiel/numérique).
    """
    buffer = BytesIO()
    page_height, page_width = A4  # Paysage A4 (297mm x 210mm)
    p = canvas.Canvas(buffer, pagesize=(page_width, page_height))

    # Palette Chromatique Haute Joaillerie
    C_BLUE_DARK = colors.HexColor('#003893')
    C_BLUE_ROYAL = colors.HexColor('#0052D4')
    C_BLUE_CYAN = colors.HexColor('#00D2FF')
    C_BLUE_SHADOW = colors.HexColor('#CBD5E1')
    C_GOLD_MAIN = colors.HexColor('#D4AF37')
    C_GOLD_LIGHT = colors.HexColor('#F9D776')
    C_GOLD_DARK = colors.HexColor('#A67C1E')
    C_TEXT_NAVY = colors.HexColor('#0F172A')
    C_TEXT_MUTED = colors.HexColor('#475569')

    # 1. Fond blanc immaculé
    p.setFillColor(colors.white)
    p.rect(0, 0, page_width, page_height, fill=1, stroke=0)

    # 2. Motifs géométriques biseautés aux 4 coins (Identique au modèle de référence)
    corner_size = 56 * mm
    shadow_offset = 6 * mm

    # Coin Haut-Gauche
    p.saveState()
    path = p.beginPath()
    path.moveTo(0, page_height - corner_size - shadow_offset)
    path.lineTo(corner_size + shadow_offset, page_height)
    path.lineTo(corner_size, page_height)
    path.lineTo(0, page_height - corner_size)
    path.close()
    p.setFillColor(C_BLUE_SHADOW)
    p.drawPath(path, fill=1, stroke=0)

    path = p.beginPath()
    path.moveTo(0, page_height - corner_size)
    path.lineTo(0, page_height)
    path.lineTo(corner_size, page_height)
    path.close()
    p.setFillColor(C_BLUE_ROYAL)
    p.drawPath(path, fill=1, stroke=0)

    path = p.beginPath()
    path.moveTo(0, page_height - corner_size * 0.75)
    path.lineTo(0, page_height)
    path.lineTo(corner_size * 0.75, page_height)
    path.close()
    p.setFillColor(C_BLUE_CYAN)
    p.drawPath(path, fill=1, stroke=0)
    p.restoreState()

    # Coin Haut-Droit
    p.saveState()
    path = p.beginPath()
    path.moveTo(page_width, page_height - corner_size - shadow_offset)
    path.lineTo(page_width - corner_size - shadow_offset, page_height)
    path.lineTo(page_width - corner_size, page_height)
    path.lineTo(page_width, page_height - corner_size)
    path.close()
    p.setFillColor(C_BLUE_SHADOW)
    p.drawPath(path, fill=1, stroke=0)

    path = p.beginPath()
    path.moveTo(page_width, page_height - corner_size)
    path.lineTo(page_width, page_height)
    path.lineTo(page_width - corner_size, page_height)
    path.close()
    p.setFillColor(C_BLUE_ROYAL)
    p.drawPath(path, fill=1, stroke=0)

    path = p.beginPath()
    path.moveTo(page_width, page_height - corner_size * 0.75)
    path.lineTo(page_width, page_height)
    path.lineTo(page_width - corner_size * 0.75, page_height)
    path.close()
    p.setFillColor(C_BLUE_CYAN)
    p.drawPath(path, fill=1, stroke=0)
    p.restoreState()

    # Coin Bas-Gauche
    p.saveState()
    path = p.beginPath()
    path.moveTo(0, corner_size + shadow_offset)
    path.lineTo(corner_size + shadow_offset, 0)
    path.lineTo(corner_size, 0)
    path.lineTo(0, corner_size)
    path.close()
    p.setFillColor(C_BLUE_SHADOW)
    p.drawPath(path, fill=1, stroke=0)

    path = p.beginPath()
    path.moveTo(0, corner_size)
    path.lineTo(0, 0)
    path.lineTo(corner_size, 0)
    path.close()
    p.setFillColor(C_BLUE_ROYAL)
    p.drawPath(path, fill=1, stroke=0)

    path = p.beginPath()
    path.moveTo(0, corner_size * 0.75)
    path.lineTo(0, 0)
    path.lineTo(corner_size * 0.75, 0)
    path.close()
    p.setFillColor(C_BLUE_CYAN)
    p.drawPath(path, fill=1, stroke=0)
    p.restoreState()

    # Coin Bas-Droit
    p.saveState()
    path = p.beginPath()
    path.moveTo(page_width, corner_size + shadow_offset)
    path.lineTo(page_width - corner_size - shadow_offset, 0)
    path.lineTo(page_width - corner_size, 0)
    path.lineTo(page_width, corner_size)
    path.close()
    p.setFillColor(C_BLUE_SHADOW)
    p.drawPath(path, fill=1, stroke=0)

    path = p.beginPath()
    path.moveTo(page_width, corner_size)
    path.lineTo(page_width, 0)
    path.lineTo(page_width - corner_size, 0)
    path.close()
    p.setFillColor(C_BLUE_ROYAL)
    p.drawPath(path, fill=1, stroke=0)

    path = p.beginPath()
    path.moveTo(page_width, corner_size * 0.75)
    path.lineTo(page_width, 0)
    path.lineTo(page_width - corner_size * 0.75, 0)
    path.close()
    p.setFillColor(C_BLUE_CYAN)
    p.drawPath(path, fill=1, stroke=0)
    p.restoreState()

    # 3. Double Cadre d'Or Géométrique aux coins chanfreinés
    m1 = 12 * mm
    cut1 = 38 * mm
    p.setStrokeColor(C_GOLD_MAIN)
    p.setLineWidth(1.8)
    bp1 = p.beginPath()
    bp1.moveTo(m1 + cut1, page_height - m1)
    bp1.lineTo(page_width - m1 - cut1, page_height - m1)
    bp1.lineTo(page_width - m1, page_height - m1 - cut1)
    bp1.lineTo(page_width - m1, m1 + cut1)
    bp1.lineTo(page_width - m1 - cut1, m1)
    bp1.lineTo(m1 + cut1, m1)
    bp1.lineTo(m1, m1 + cut1)
    bp1.lineTo(m1, page_height - m1 - cut1)
    bp1.close()
    p.drawPath(bp1, fill=0, stroke=1)

    m2 = 14.5 * mm
    cut2 = 36 * mm
    p.setStrokeColor(C_GOLD_LIGHT)
    p.setLineWidth(0.7)
    bp2 = p.beginPath()
    bp2.moveTo(m2 + cut2, page_height - m2)
    bp2.lineTo(page_width - m2 - cut2, page_height - m2)
    bp2.lineTo(page_width - m2, page_height - m2 - cut2)
    bp2.lineTo(page_width - m2, m2 + cut2)
    bp2.lineTo(page_width - m2 - cut2, m2)
    bp2.lineTo(m2 + cut2, m2)
    bp2.lineTo(m2, m2 + cut2)
    bp2.lineTo(m2, page_height - m2 - cut2)
    bp2.close()
    p.drawPath(bp2, fill=0, stroke=1)

    # 4. En-tête : Logos officiels (UY1 En premier et agrandi, puis COMSAS)
    uy1_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'uy1.png')
    comsas_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'comsas.png')
    
    logo_top_y = page_height - 35 * mm
    logo_size = 22 * mm

    # Logo Université de Yaoundé 1 (Agrandit et placé avant COMSAS)
    if os.path.exists(uy1_path):
        try:
            p.drawImage(ImageReader(uy1_path), 32 * mm, logo_top_y, width=logo_size, height=logo_size, mask='auto', preserveAspectRatio=True)
        except Exception:
            pass

    # Logo COMSAS (À droite de l'en-tête)
    if os.path.exists(comsas_path):
        try:
            p.drawImage(ImageReader(comsas_path), page_width - 32 * mm - logo_size, logo_top_y, width=logo_size, height=logo_size, mask='auto', preserveAspectRatio=True)
        except Exception:
            pass

    # Titre institutionnel au centre
    p.setFont("Helvetica-Bold", 10.5)
    p.setFillColor(C_TEXT_NAVY)
    p.drawCentredString(page_width / 2, page_height - 21 * mm, "UNIVERSITÉ DE YAOUNDÉ 1 • FACULTÉ DES SCIENCES")
    p.setFont("Helvetica", 8.5)
    p.setFillColor(C_TEXT_MUTED)
    p.drawCentredString(page_width / 2, page_height - 26 * mm, "Département d'Informatique • Computer Science Association (COMSAS)")

    # 5. Grand Titre "CERTIFICAT" (Bleu Royal Majestueux avec Auto-Scale)
    cert_title = (getattr(event, 'certificate_title', None) or "CERTIFICAT").upper()
    title_fs = 34
    max_title_w = page_width - 95 * mm
    while stringWidth(cert_title, "Helvetica-Bold", title_fs) > max_title_w and title_fs > 15:
        title_fs -= 1

    p.setFont("Helvetica-Bold", title_fs)
    p.setFillColor(C_BLUE_ROYAL)
    p.drawCentredString(page_width / 2, page_height - 43 * mm, cert_title)

    # 6. Ruban Doré / Bannière de Prestige avec encoches
    ribbon_y = page_height - 53 * mm
    ribbon_w = 115 * mm
    ribbon_h = 7.5 * mm
    rx = page_width / 2 - ribbon_w / 2

    p.saveState()
    # Queue gauche
    p.setFillColor(C_GOLD_DARK)
    tail_l = p.beginPath()
    tail_l.moveTo(rx, ribbon_y)
    tail_l.lineTo(rx - 8 * mm, ribbon_y - 2 * mm)
    tail_l.lineTo(rx - 4 * mm, ribbon_y + ribbon_h / 2)
    tail_l.lineTo(rx - 8 * mm, ribbon_y + ribbon_h + 2 * mm)
    tail_l.lineTo(rx, ribbon_y + ribbon_h)
    tail_l.close()
    p.drawPath(tail_l, fill=1, stroke=0)

    # Queue droite
    p.setFillColor(C_GOLD_DARK)
    tail_r = p.beginPath()
    tail_r.moveTo(rx + ribbon_w, ribbon_y)
    tail_r.lineTo(rx + ribbon_w + 8 * mm, ribbon_y - 2 * mm)
    tail_r.lineTo(rx + ribbon_w + 4 * mm, ribbon_y + ribbon_h / 2)
    tail_r.lineTo(rx + ribbon_w + 8 * mm, ribbon_y + ribbon_h + 2 * mm)
    tail_r.lineTo(rx + ribbon_w, ribbon_y + ribbon_h)
    tail_r.close()
    p.drawPath(tail_r, fill=1, stroke=0)

    # Corps central du ruban
    p.setFillColor(C_GOLD_MAIN)
    p.rect(rx, ribbon_y, ribbon_w, ribbon_h, fill=1, stroke=0)
    p.setStrokeColor(C_GOLD_LIGHT)
    p.setLineWidth(0.6)
    p.rect(rx + 0.5 * mm, ribbon_y + 0.5 * mm, ribbon_w - 1 * mm, ribbon_h - 1 * mm, fill=0, stroke=1)

    # Texte du ruban
    cert_subtitle = (getattr(event, 'certificate_subtitle', None) or "DE PARTICIPATION ET D'EXCELLENCE").upper()
    p.setFont("Helvetica-Bold", 8.5)
    p.setFillColor(colors.white)
    p.drawCentredString(page_width / 2, ribbon_y + 2.2 * mm, cert_subtitle)
    p.restoreState()

    # 7. Mention Récipiendaire
    p.setFont("Helvetica-Oblique", 11)
    p.setFillColor(C_TEXT_MUTED)
    p.drawCentredString(page_width / 2, page_height - 67 * mm, "Ce certificat est fièrement décerné à :")

    # 8. Nom du participant (Police Calligraphique Décorative GreatVibes)
    nom_participant = participant_data.get('nom_prenom', 'Patrice Nguekam Dassi')
    p.setFillColor(C_TEXT_NAVY)

    font_name = "GreatVibes" if ("GreatVibes" in pdfmetrics.getRegisteredFontNames()) else "Helvetica-Bold"
    name_font_size = 44
    max_w = page_width - 70 * mm
    while stringWidth(nom_participant, font_name, name_font_size) > max_w and name_font_size > 22:
        name_font_size -= 2

    p.setFont(font_name, name_font_size)
    p.drawCentredString(page_width / 2, page_height - 84 * mm, nom_participant)

    # Filet doré décoratif avec diamant central sous le nom
    line_y = page_height - 90 * mm
    line_half = 55 * mm
    p.setStrokeColor(C_GOLD_MAIN)
    p.setLineWidth(1)
    p.line(page_width / 2 - line_half, line_y, page_width / 2 - 3 * mm, line_y)
    p.line(page_width / 2 + 3 * mm, line_y, page_width / 2 + line_half, line_y)

    diamond = p.beginPath()
    diamond.moveTo(page_width / 2, line_y + 2 * mm)
    diamond.lineTo(page_width / 2 + 2.5 * mm, line_y)
    diamond.lineTo(page_width / 2, line_y - 2 * mm)
    diamond.lineTo(page_width / 2 - 2.5 * mm, line_y)
    diamond.close()
    p.setFillColor(C_GOLD_MAIN)
    p.drawPath(diamond, fill=1, stroke=0)

    # 9. Texte du certificat / Corps
    p.setFont("Helvetica", 10.5)
    p.setFillColor(C_TEXT_MUTED)
    
    event_title = getattr(event, 'title_fr', 'Événement Officiel')
    texte_principal = getattr(event, 'certificate_main_text', '') or f"pour sa participation active et remarquable aux travaux et ateliers pratiques de l'événement \"{event_title}\" organisé par le Club Informatique COMSAS."
    
    words = texte_principal.split()
    lignes, cur_l = [], ""
    max_body_w = page_width - 80 * mm
    for w in words:
        if stringWidth(cur_l + " " + w, "Helvetica", 10.5) < max_body_w:
            cur_l += (" " + w if cur_l else w)
        else:
            lignes.append(cur_l)
            cur_l = w
    if cur_l:
        lignes.append(cur_l)

    body_y = page_height - 101 * mm
    for l in lignes[:3]:
        p.drawCentredString(page_width / 2, body_y, l)
        body_y -= 5.5 * mm

    # 10. Sceau d'or central (Médaille d'honneur à 24 pétales)
    seal_x = page_width / 2
    seal_y = 38 * mm
    seal_r = 13 * mm

    p.saveState()
    p.setFillColor(C_GOLD_MAIN)
    seal_path = p.beginPath()
    num_petals = 24
    for i in range(num_petals * 2):
        angle = i * (math.pi / num_petals)
        r = seal_r if (i % 2 == 0) else (seal_r - 2.2 * mm)
        px = seal_x + r * math.cos(angle)
        py = seal_y + r * math.sin(angle)
        if i == 0:
            seal_path.moveTo(px, py)
        else:
            seal_path.lineTo(px, py)
    seal_path.close()
    p.drawPath(seal_path, fill=1, stroke=0)

    # Disque intérieur or clair
    p.setFillColor(C_GOLD_LIGHT)
    p.circle(seal_x, seal_y, seal_r - 2.8 * mm, fill=1, stroke=0)
    p.setStrokeColor(C_GOLD_DARK)
    p.setLineWidth(0.8)
    p.circle(seal_x, seal_y, seal_r - 3.8 * mm, fill=0, stroke=1)

    # Étoile d'honneur dorée
    p.setFont("Helvetica-Bold", 11)
    p.setFillColor(C_GOLD_DARK)
    p.drawCentredString(seal_x, seal_y - 1.2 * mm, "★")
    p.restoreState()

    # 11. Configuration des signataires (Président & éventuel 2ème signataire en présentiel/numérique)
    second_enabled = getattr(event, 'second_signatory_enabled', False)
    pos_mode = getattr(event, 'signatories_position', 'sig1_left_sig2_right')

    sig1_name = getattr(event, 'certificate_president_name', 'Borel Henri NGUIMEZAP') or "Borel Henri NGUIMEZAP"
    sig1_title = getattr(event, 'certificate_president_title', 'Le Président du COMS.A.S') or "Le Président du COMS.A.S"
    sig1_digital = getattr(event, 'signatory1_is_digital', True)
    
    # Signature image path
    sig1_img_path = None
    if getattr(event, 'president_signature', None) and hasattr(event.president_signature, 'path') and os.path.exists(event.president_signature.path):
        sig1_img_path = event.president_signature.path
    else:
        default_sig = os.path.join(settings.BASE_DIR, 'static', 'images', 'signature.png')
        if os.path.exists(default_sig):
            sig1_img_path = default_sig

    sig2_name = getattr(event, 'signatory2_name', '') or "Pr. Chef de Département"
    sig2_title = getattr(event, 'signatory2_title', "Le Chef de Département d'Informatique") or "Le Chef de Département d'Informatique"
    sig2_digital = getattr(event, 'signatory2_is_digital', False)
    sig2_img_path = None
    if getattr(event, 'signatory2_signature', None) and hasattr(event.signatory2_signature, 'path') and os.path.exists(event.signatory2_signature.path):
        sig2_img_path = event.signatory2_signature.path

    date_str = participant_data.get('date_str', timezone.now().strftime('%d/%m/%Y'))
    location_prefix = getattr(event, 'certificate_location_text', 'Fait à Yaoundé, le') or "Fait à Yaoundé, le"

    # Données QR Code
    uuid_val = participant_data.get('uuid', 'CERT-UY1-2026-COMSAS')
    verify_url = participant_data.get('verify_url') or f"{getattr(settings, 'SITE_URL', 'https://comsas-uy1.com')}/verify/{uuid_val}"
    qr = qrcode.QRCode(box_size=4, border=0)
    qr.add_data(verify_url)
    qr.make(fit=True)
    qr_buf = BytesIO()
    qr.make_image(fill_color="#003893", back_color="white").save(qr_buf, 'PNG')
    qr_buf.seek(0)
    qr_img = ImageReader(qr_buf)

    if second_enabled and pos_mode != 'centered':
        # 2 SIGNATAIRES (Gauche & Droite)
        if pos_mode == 'sig1_right_sig2_left':
            left_info = (sig2_name, sig2_title, sig2_digital, sig2_img_path)
            right_info = (sig1_name, sig1_title, sig1_digital, sig1_img_path)
        else:  # sig1_left_sig2_right
            left_info = (sig1_name, sig1_title, sig1_digital, sig1_img_path)
            right_info = (sig2_name, sig2_title, sig2_digital, sig2_img_path)

        # GAUCHE
        left_x = 65 * mm
        p.setStrokeColor(C_TEXT_NAVY)
        p.setLineWidth(1)
        p.line(left_x - 30 * mm, 33 * mm, left_x + 30 * mm, 33 * mm)

        if left_info[2] and left_info[3] and os.path.exists(left_info[3]):
            try:
                p.drawImage(ImageReader(left_info[3]), left_x - 22 * mm, 34 * mm, width=44 * mm, height=20 * mm, mask='auto', preserveAspectRatio=True)
            except Exception:
                pass
        elif not left_info[2]:
            p.setFont("Helvetica-Oblique", 7.5)
            p.setFillColor(C_TEXT_MUTED)
            p.drawCentredString(left_x, 35 * mm, "(Signature et Cachet manuscrits)")

        p.setFont("Helvetica-Bold", 10)
        p.setFillColor(C_TEXT_NAVY)
        p.drawCentredString(left_x, 27 * mm, left_info[1])
        p.setFont("Helvetica", 9)
        p.setFillColor(C_TEXT_MUTED)
        p.drawCentredString(left_x, 22 * mm, left_info[0])

        # DROITE
        right_x = page_width - 65 * mm
        p.setStrokeColor(C_TEXT_NAVY)
        p.setLineWidth(1)
        p.line(right_x - 30 * mm, 33 * mm, right_x + 30 * mm, 33 * mm)

        if right_info[2] and right_info[3] and os.path.exists(right_info[3]):
            try:
                p.drawImage(ImageReader(right_info[3]), right_x - 22 * mm, 34 * mm, width=44 * mm, height=20 * mm, mask='auto', preserveAspectRatio=True)
            except Exception:
                pass
        elif not right_info[2]:
            p.setFont("Helvetica-Oblique", 7.5)
            p.setFillColor(C_TEXT_MUTED)
            p.drawCentredString(right_x, 35 * mm, "(Signature et Cachet manuscrits)")

        p.setFont("Helvetica-Bold", 10)
        p.setFillColor(C_TEXT_NAVY)
        p.drawCentredString(right_x, 27 * mm, right_info[1])
        p.setFont("Helvetica", 9)
        p.setFillColor(C_TEXT_MUTED)
        p.drawCentredString(right_x, 22 * mm, right_info[0])

        # Date & Lieu sous le sceau central
        p.setFont("Helvetica-Bold", 9.5)
        p.setFillColor(C_TEXT_NAVY)
        p.drawCentredString(seal_x, 20 * mm, f"{location_prefix} {date_str}")
        p.setFont("Helvetica", 6.5)
        p.setFillColor(C_BLUE_ROYAL)
        p.drawCentredString(seal_x, 16 * mm, f"Vérifiable en ligne • ID: {str(uuid_val)[:18]}")

    else:
        # 1 SEUL SIGNATAIRE
        # Mention date et lieu à gauche
        left_block_x = 38 * mm
        p.setFont("Helvetica-Bold", 10)
        p.setFillColor(C_TEXT_NAVY)
        p.drawString(left_block_x, 38 * mm, f"{location_prefix} {date_str}")
        p.setFont("Helvetica", 8)
        p.setFillColor(C_TEXT_MUTED)
        p.drawString(left_block_x, 33 * mm, "Faculté des Sciences • Université de Yaoundé 1")
        p.setStrokeColor(C_GOLD_MAIN)
        p.setLineWidth(0.8)
        p.line(left_block_x, 30 * mm, left_block_x + 55 * mm, 30 * mm)

        # QR Code intégré élégamment sous la date
        qr_mini_s = 13 * mm
        p.drawImage(qr_img, left_block_x, 15 * mm, width=qr_mini_s, height=qr_mini_s)
        p.setFont("Helvetica-Bold", 6)
        p.setFillColor(C_BLUE_ROYAL)
        p.drawString(left_block_x + qr_mini_s + 2.5 * mm, 23 * mm, "AUTHENTICITÉ VÉRIFIABLE EN LIGNE")
        p.setFont("Helvetica", 5.5)
        p.setFillColor(C_TEXT_MUTED)
        p.drawString(left_block_x + qr_mini_s + 2.5 * mm, 18.5 * mm, f"ID: {str(uuid_val)[:20]}")

        # Signataire à droite
        sig_x = page_width - 65 * mm
        p.setStrokeColor(C_TEXT_NAVY)
        p.setLineWidth(1)
        p.line(sig_x - 32 * mm, 33 * mm, sig_x + 32 * mm, 33 * mm)

        if sig1_digital and sig1_img_path and os.path.exists(sig1_img_path):
            try:
                p.drawImage(ImageReader(sig1_img_path), sig_x - 24 * mm, 34 * mm, width=48 * mm, height=22 * mm, mask='auto', preserveAspectRatio=True)
            except Exception:
                pass
        elif not sig1_digital:
            p.setFont("Helvetica-Oblique", 7.5)
            p.setFillColor(C_TEXT_MUTED)
            p.drawCentredString(sig_x, 35 * mm, "(Signature et Cachet manuscrits)")

        p.setFont("Helvetica-Bold", 10.5)
        p.setFillColor(C_TEXT_NAVY)
        p.drawCentredString(sig_x, 27 * mm, sig1_title)
        p.setFont("Helvetica", 9.5)
        p.setFillColor(C_TEXT_MUTED)
        p.drawCentredString(sig_x, 22 * mm, sig1_name)

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer


def generate_certificate(registration):
    """
    Génère et sauvegarde le PDF de l'attestation pour un participant inscrit.
    """
    event = registration.event
    if not getattr(event, 'certificate_enabled', True):
        return None

    verify_url = f"{getattr(settings, 'SITE_URL', 'https://comsas-uy1.com')}{reverse('ticket_verify', kwargs={'uuid': registration.uuid})}"
    
    participant_data = {
        'nom_prenom': registration.nom_prenom,
        'uuid': registration.uuid,
        'verify_url': verify_url,
        'date_str': timezone.now().strftime('%d/%m/%Y'),
    }

    buffer = render_certificate_pdf(event, participant_data)
    
    if registration.certificate_pdf:
        registration.certificate_pdf.delete(save=False)
    
    registration.certificate_pdf.save(f'certificate_{registration.uuid}.pdf', File(buffer), save=True)
    return registration.certificate_pdf.url


def generate_preview_certificate(event):
    """
    Génère un PDF d'attestation de prévisualisation avec des données de démonstration.
    """
    participant_data = {
        'nom_prenom': 'Patrice Nguekam Dassi',
        'uuid': 'PREVIEW-CERT-2026-COMSAS',
        'verify_url': f"{getattr(settings, 'SITE_URL', 'https://comsas-uy1.com')}/verify/preview",
        'date_str': timezone.now().strftime('%d/%m/%Y'),
    }
    return render_certificate_pdf(event, participant_data)
