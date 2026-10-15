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

# Enregistrement de la police calligraphique GreatVibes
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
    Rendu vectoriel d'élite de l'attestation de prestige.
    Équilibrage vertical parfait (aucun vide au milieu),
    marges intérieures sécurisées (aucun élément ne touche les bordures),
    cachets/signatures posés SUR les lignes, logo UY1 mis en valeur en premier.
    """
    buffer = BytesIO()
    page_height, page_width = A4  # 297mm x 210mm
    p = canvas.Canvas(buffer, pagesize=(page_width, page_height))

    # Palette Chromatique
    C_BLUE_ROYAL = colors.HexColor('#0052D4')
    C_BLUE_CYAN = colors.HexColor('#00D2FF')
    C_BLUE_SHADOW = colors.HexColor('#CBD5E1')
    C_GOLD_MAIN = colors.HexColor('#D4AF37')
    C_GOLD_LIGHT = colors.HexColor('#F9D776')
    C_GOLD_DARK = colors.HexColor('#A67C1E')
    C_TEXT_NAVY = colors.HexColor('#0F172A')
    C_TEXT_MUTED = colors.HexColor('#475569')

    # 1. Fond blanc pur
    p.setFillColor(colors.white)
    p.rect(0, 0, page_width, page_height, fill=1, stroke=0)

    # 2. Motifs géométriques d'angles biseautés bleu/cyan (Reproduction fidèle de la maquette)
    corner_size = 52 * mm
    shadow_offset = 5.5 * mm

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

    # 3. Double Cadre d'Or aux angles biseautés à 45°
    m1 = 11 * mm
    cut1 = 36 * mm
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

    m2 = 13.5 * mm
    cut2 = 34 * mm
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

    # 4. En-tête Institutionnel & Logos (Parfaitement positionnés sans toucher les bords)
    uy1_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'uy1.png')
    comsas_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'comsas.png')
    
    logo_size = 18 * mm
    logo_y = 168 * mm

    # Logo Université de Yaoundé 1 (À gauche, net et bien dégagé du chanfrein)
    if os.path.exists(uy1_path):
        try:
            p.drawImage(ImageReader(uy1_path), 50 * mm, logo_y, width=logo_size, height=logo_size, mask='auto', preserveAspectRatio=True)
        except Exception:
            pass

    # Logo COMSAS (À droite, dégagé du chanfrein)
    if os.path.exists(comsas_path):
        try:
            p.drawImage(ImageReader(comsas_path), page_width - 50 * mm - logo_size, logo_y, width=logo_size, height=logo_size, mask='auto', preserveAspectRatio=True)
        except Exception:
            pass

    # Texte de l'Université et Faculté au centre
    p.setFont("Helvetica-Bold", 9.5)
    p.setFillColor(C_TEXT_NAVY)
    p.drawCentredString(page_width / 2, 178 * mm, "UNIVERSITÉ DE YAOUNDÉ 1 • FACULTÉ DES SCIENCES")
    p.setFont("Helvetica", 8)
    p.setFillColor(C_TEXT_MUTED)
    p.drawCentredString(page_width / 2, 173 * mm, "Département d'Informatique • Computer Science Association (COMSAS)")

    # 5. Grand Titre "CERTIFICAT" ou "ATTESTATION"
    cert_title = (getattr(event, 'certificate_title', None) or "CERTIFICAT").upper()
    title_fs = 28
    max_title_w = page_width - 120 * mm
    while stringWidth(cert_title, "Helvetica-Bold", title_fs) > max_title_w and title_fs > 16:
        title_fs -= 1

    p.setFont("Helvetica-Bold", title_fs)
    p.setFillColor(C_BLUE_ROYAL)
    p.drawCentredString(page_width / 2, 156 * mm, cert_title)

    # 6. Ruban Doré / Bannière de Prestige
    ribbon_y = 143 * mm
    ribbon_w = 118 * mm
    ribbon_h = 7.5 * mm
    rx = page_width / 2 - ribbon_w / 2

    p.saveState()
    p.setFillColor(C_GOLD_DARK)
    tail_l = p.beginPath()
    tail_l.moveTo(rx, ribbon_y)
    tail_l.lineTo(rx - 8 * mm, ribbon_y - 2 * mm)
    tail_l.lineTo(rx - 4 * mm, ribbon_y + ribbon_h / 2)
    tail_l.lineTo(rx - 8 * mm, ribbon_y + ribbon_h + 2 * mm)
    tail_l.lineTo(rx, ribbon_y + ribbon_h)
    tail_l.close()
    p.drawPath(tail_l, fill=1, stroke=0)

    tail_r = p.beginPath()
    tail_r.moveTo(rx + ribbon_w, ribbon_y)
    tail_r.lineTo(rx + ribbon_w + 8 * mm, ribbon_y - 2 * mm)
    tail_r.lineTo(rx + ribbon_w + 4 * mm, ribbon_y + ribbon_h / 2)
    tail_r.lineTo(rx + ribbon_w + 8 * mm, ribbon_y + ribbon_h + 2 * mm)
    tail_r.lineTo(rx + ribbon_w, ribbon_y + ribbon_h)
    tail_r.close()
    p.drawPath(tail_r, fill=1, stroke=0)

    p.setFillColor(C_GOLD_MAIN)
    p.rect(rx, ribbon_y, ribbon_w, ribbon_h, fill=1, stroke=0)
    p.setStrokeColor(C_GOLD_LIGHT)
    p.setLineWidth(0.6)
    p.rect(rx + 0.5 * mm, ribbon_y + 0.5 * mm, ribbon_w - 1 * mm, ribbon_h - 1 * mm, fill=0, stroke=1)

    cert_subtitle = (getattr(event, 'certificate_subtitle', None) or "DE PARTICIPATION ET D'EXCELLENCE").upper()
    p.setFont("Helvetica-Bold", 8.5)
    p.setFillColor(colors.white)
    p.drawCentredString(page_width / 2, ribbon_y + 2.2 * mm, cert_subtitle)
    p.restoreState()

    # 7. Mention Récipiendaire
    p.setFont("Helvetica-Oblique", 11)
    p.setFillColor(C_TEXT_MUTED)
    p.drawCentredString(page_width / 2, 128 * mm, "Ce certificat est fièrement décerné à :")

    # 8. Nom du Participant (Police Calligraphique GreatVibes centrée avec grâce)
    nom_participant = participant_data.get('nom_prenom', 'Patrice Nguekam Dassi')
    p.setFillColor(C_TEXT_NAVY)

    font_name = "GreatVibes" if ("GreatVibes" in pdfmetrics.getRegisteredFontNames()) else "Helvetica-Bold"
    name_font_size = 42
    max_w = page_width - 90 * mm
    while stringWidth(nom_participant, font_name, name_font_size) > max_w and name_font_size > 22:
        name_font_size -= 2

    p.setFont(font_name, name_font_size)
    p.drawCentredString(page_width / 2, 108 * mm, nom_participant)

    # Filet doré avec diamant central sous le nom
    line_y = 101 * mm
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

    # 9. Texte du certificat / Corps (Bien placé dans la moitié inférieure)
    p.setFont("Helvetica", 10.5)
    p.setFillColor(C_TEXT_MUTED)
    
    event_title = getattr(event, 'title_fr', 'Événement Officiel')
    texte_principal = getattr(event, 'certificate_main_text', '') or f"pour sa participation active et remarquable aux travaux et ateliers pratiques de l'événement \"{event_title}\" organisé par le Club Informatique COMSAS."
    
    words = texte_principal.split()
    lignes, cur_l = [], ""
    max_body_w = page_width - 90 * mm
    for w in words:
        if stringWidth(cur_l + " " + w, "Helvetica", 10.5) < max_body_w:
            cur_l += (" " + w if cur_l else w)
        else:
            lignes.append(cur_l)
            cur_l = w
    if cur_l:
        lignes.append(cur_l)

    body_y = 88 * mm
    for l in lignes[:3]:
        p.drawCentredString(page_width / 2, body_y, l)
        body_y -= 5.5 * mm

    # 10. Sceau d'or central (Médaille d'honneur à 24 pétales)
    seal_x = page_width / 2
    seal_y = 48 * mm
    seal_r = 13.5 * mm

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

    p.setFillColor(C_GOLD_LIGHT)
    p.circle(seal_x, seal_y, seal_r - 2.8 * mm, fill=1, stroke=0)
    p.setStrokeColor(C_GOLD_DARK)
    p.setLineWidth(0.8)
    p.circle(seal_x, seal_y, seal_r - 3.8 * mm, fill=0, stroke=1)

    p.setFont("Helvetica-Bold", 11)
    p.setFillColor(C_GOLD_DARK)
    p.drawCentredString(seal_x, seal_y - 1.2 * mm, "★")
    p.restoreState()

    # 11. Configuration des signataires (Positionnement propre avec cachets posés SUR les lignes)
    second_enabled = getattr(event, 'second_signatory_enabled', False)
    pos_mode = getattr(event, 'signatories_position', 'sig1_left_sig2_right')

    sig1_name = getattr(event, 'certificate_president_name', 'Borel Henri NGUIMEZAP') or "Borel Henri NGUIMEZAP"
    sig1_title = getattr(event, 'certificate_president_title', 'Le Président du COMS.A.S') or "Le Président du COMS.A.S"
    sig1_digital = getattr(event, 'signatory1_is_digital', True)
    
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

    # Hauteur de référence de la ligne de signature
    sig_line_y = 42 * mm

    if second_enabled and pos_mode != 'centered':
        # --- 2 SIGNATAIRES (Gauche & Droite) ---
        if pos_mode == 'sig1_right_sig2_left':
            left_info = (sig2_name, sig2_title, sig2_digital, sig2_img_path)
            right_info = (sig1_name, sig1_title, sig1_digital, sig1_img_path)
        else:  # sig1_left_sig2_right
            left_info = (sig1_name, sig1_title, sig1_digital, sig1_img_path)
            right_info = (sig2_name, sig2_title, sig2_digital, sig2_img_path)

        # GAUCHE : Ligne de signature
        left_x = 72 * mm
        p.setStrokeColor(C_TEXT_NAVY)
        p.setLineWidth(1)
        p.line(left_x - 30 * mm, sig_line_y, left_x + 30 * mm, sig_line_y)

        # Le cachet / signature est posé AU-DESSUS de la ligne
        if left_info[2] and left_info[3] and os.path.exists(left_info[3]):
            try:
                p.drawImage(ImageReader(left_info[3]), left_x - 22 * mm, sig_line_y + 1 * mm, width=44 * mm, height=22 * mm, mask='auto', preserveAspectRatio=True)
            except Exception:
                pass
        elif not left_info[2]:
            p.setFont("Helvetica-Oblique", 7.5)
            p.setFillColor(C_TEXT_MUTED)
            p.drawCentredString(left_x, sig_line_y + 4 * mm, "(Signature et Cachet manuscrits)")

        # Titre et Nom sous la ligne
        p.setFont("Helvetica-Bold", 9.5)
        p.setFillColor(C_TEXT_NAVY)
        p.drawCentredString(left_x, sig_line_y - 6 * mm, left_info[1])
        p.setFont("Helvetica", 8.5)
        p.setFillColor(C_TEXT_MUTED)
        p.drawCentredString(left_x, sig_line_y - 11 * mm, left_info[0])

        # DROITE : Ligne de signature
        right_x = page_width - 72 * mm
        p.setStrokeColor(C_TEXT_NAVY)
        p.setLineWidth(1)
        p.line(right_x - 30 * mm, sig_line_y, right_x + 30 * mm, sig_line_y)

        # Le cachet / signature est posé AU-DESSUS de la ligne
        if right_info[2] and right_info[3] and os.path.exists(right_info[3]):
            try:
                p.drawImage(ImageReader(right_info[3]), right_x - 22 * mm, sig_line_y + 1 * mm, width=44 * mm, height=22 * mm, mask='auto', preserveAspectRatio=True)
            except Exception:
                pass
        elif not right_info[2]:
            p.setFont("Helvetica-Oblique", 7.5)
            p.setFillColor(C_TEXT_MUTED)
            p.drawCentredString(right_x, sig_line_y + 4 * mm, "(Signature et Cachet manuscrits)")

        # Titre et Nom sous la ligne
        p.setFont("Helvetica-Bold", 9.5)
        p.setFillColor(C_TEXT_NAVY)
        p.drawCentredString(right_x, sig_line_y - 6 * mm, right_info[1])
        p.setFont("Helvetica", 8.5)
        p.setFillColor(C_TEXT_MUTED)
        p.drawCentredString(right_x, sig_line_y - 11 * mm, right_info[0])

        # Date & Lieu bien alignés sous le sceau central
        p.setFont("Helvetica-Bold", 9)
        p.setFillColor(C_TEXT_NAVY)
        p.drawCentredString(seal_x, 26 * mm, f"{location_prefix} {date_str}")
        p.setFont("Helvetica", 6.5)
        p.setFillColor(C_BLUE_ROYAL)
        uuid_val = participant_data.get('uuid', 'CERT-UY1-2026')
        p.drawCentredString(seal_x, 21 * mm, f"Vérification officielle • ID: {str(uuid_val)[:20]}")

    else:
        # --- 1 SEUL SIGNATAIRE ---
        # Date & Lieu à gauche avec trait de présentation
        left_x = 72 * mm
        p.setFont("Helvetica-Bold", 9.5)
        p.setFillColor(C_TEXT_NAVY)
        p.drawString(left_x - 30 * mm, sig_line_y + 7 * mm, f"{location_prefix} {date_str}")
        p.setStrokeColor(C_GOLD_MAIN)
        p.setLineWidth(1)
        p.line(left_x - 30 * mm, sig_line_y, left_x + 30 * mm, sig_line_y)
        p.setFont("Helvetica", 8)
        p.setFillColor(C_TEXT_MUTED)
        p.drawString(left_x - 30 * mm, sig_line_y - 6 * mm, "Faculté des Sciences • Université de Yaoundé 1")
        
        uuid_val = participant_data.get('uuid', 'CERT-UY1-2026')
        p.setFont("Helvetica", 6.5)
        p.setFillColor(C_BLUE_ROYAL)
        p.drawString(left_x - 30 * mm, sig_line_y - 11 * mm, f"Vérifiable en ligne • ID: {str(uuid_val)[:18]}")

        # Signataire à droite
        right_x = page_width - 72 * mm
        p.setStrokeColor(C_TEXT_NAVY)
        p.setLineWidth(1)
        p.line(right_x - 30 * mm, sig_line_y, right_x + 30 * mm, sig_line_y)

        # Cachet/Signature AU-DESSUS de la ligne
        if sig1_digital and sig1_img_path and os.path.exists(sig1_img_path):
            try:
                p.drawImage(ImageReader(sig1_img_path), right_x - 22 * mm, sig_line_y + 1 * mm, width=44 * mm, height=22 * mm, mask='auto', preserveAspectRatio=True)
            except Exception:
                pass
        elif not sig1_digital:
            p.setFont("Helvetica-Oblique", 7.5)
            p.setFillColor(C_TEXT_MUTED)
            p.drawCentredString(right_x, sig_line_y + 4 * mm, "(Signature et Cachet manuscrits)")

        # Titre et Nom sous la ligne (SANS doublon !)
        p.setFont("Helvetica-Bold", 9.5)
        p.setFillColor(C_TEXT_NAVY)
        p.drawCentredString(right_x, sig_line_y - 6 * mm, sig1_title)
        p.setFont("Helvetica", 8.5)
        p.setFillColor(C_TEXT_MUTED)
        p.drawCentredString(right_x, sig_line_y - 11 * mm, sig1_name)

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer


def generate_certificate(registration):
    """Génère et sauvegarde l'attestation officielle pour un participant"""
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
    """Génère un PDF d'attestation de démonstration pour la prévisualisation admin"""
    participant_data = {
        'nom_prenom': 'Patrice Nguekam Dassi',
        'uuid': 'PREVIEW-CERT-2026-COMSAS',
        'verify_url': f"{getattr(settings, 'SITE_URL', 'https://comsas-uy1.com')}/verify/preview",
        'date_str': timezone.now().strftime('%d/%m/%Y'),
    }
    return render_certificate_pdf(event, participant_data)
