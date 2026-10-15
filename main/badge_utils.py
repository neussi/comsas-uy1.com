import os
import qrcode
from io import BytesIO
from django.core.files import File
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A6
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth
from django.conf import settings
from django.urls import reverse
from PIL import Image, ImageOps, ImageDraw


def create_circular_mask(image_path, size=(500, 500)):
    """Crée un masque circulaire haute résolution pour la photo du participant"""
    try:
        if not image_path or not os.path.exists(image_path):
            return None
        img = Image.open(image_path).convert("RGBA")
        img = ImageOps.fit(img, size, centering=(0.5, 0.5))
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + size, fill=255)
        output = Image.new('RGBA', size, (0, 0, 0, 0))
        output.paste(img, (0, 0), mask=mask)
        return output
    except Exception:
        return None


def render_badge_pdf(event, participant_data):
    """
    Rendu du Badge A6 Portrait ultra-prestige.
    En-tête avec UY1 agrandi avant COMSAS, cadre or et bleu royal,
    photo en anneau doré, rôle personnalisable et signature officielle.
    """
    buffer = BytesIO()
    width, height = A6  # 105mm x 148mm
    p = canvas.Canvas(buffer, pagesize=A6)

    # Palette Prestige
    C_NAVY_DARK = colors.HexColor('#0A1128')
    C_BLUE_ROYAL = colors.HexColor('#0052D4')
    C_BLUE_CYAN = colors.HexColor('#00D2FF')
    C_GOLD_MAIN = colors.HexColor('#D4AF37')
    C_GOLD_LIGHT = colors.HexColor('#F9D776')
    C_BG_LIGHT = colors.HexColor('#F8FAFC')
    C_TEXT_MUTED = colors.HexColor('#64748B')

    # 1. Fond général
    p.setFillColor(C_BG_LIGHT)
    p.rect(0, 0, width, height, fill=1, stroke=0)

    # 2. Bandeau supérieur géométrique Prestige
    top_h = 32 * mm
    p.saveState()
    # Gradient simulant Royal Blue -> Navy
    p.setFillColor(C_NAVY_DARK)
    p.rect(0, height - top_h, width, top_h, fill=1, stroke=0)

    # Triangle cyan d'accent en haut à droite
    t_path = p.beginPath()
    t_path.moveTo(width, height)
    t_path.lineTo(width - 35 * mm, height)
    t_path.lineTo(width, height - 25 * mm)
    t_path.close()
    p.setFillColor(C_BLUE_ROYAL)
    p.drawPath(t_path, fill=1, stroke=0)

    # Liseré doré de séparation
    p.setStrokeColor(C_GOLD_MAIN)
    p.setLineWidth(1.8)
    p.line(0, height - top_h, width, height - top_h)
    p.setStrokeColor(C_GOLD_LIGHT)
    p.setLineWidth(0.6)
    p.line(0, height - top_h - 1 * mm, width, height - top_h - 1 * mm)
    p.restoreState()

    # 3. Logos en-tête (UY1 Agrandit et placé EN PREMIER à gauche, COMSAS à droite)
    uy1_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'uy1.png')
    comsas_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'comsas.png')

    logo_h = 16 * mm
    logo_y = height - 20 * mm

    # Logo UY1 (Premier, agrandi et net)
    if os.path.exists(uy1_path):
        try:
            p.drawImage(ImageReader(uy1_path), 8 * mm, logo_y - 2 * mm, width=16 * mm, height=16 * mm, mask='auto', preserveAspectRatio=True)
        except Exception:
            pass

    # Logo COMSAS (À droite)
    if os.path.exists(comsas_path):
        try:
            p.drawImage(ImageReader(comsas_path), width - 24 * mm, logo_y - 2 * mm, width=16 * mm, height=16 * mm, mask='auto', preserveAspectRatio=True)
        except Exception:
            pass

    # Titre institutionnel au centre du bandeau
    p.setFont("Helvetica-Bold", 7.5)
    p.setFillColor(colors.white)
    p.drawCentredString(width / 2, height - 10 * mm, "UNIVERSITÉ DE YAOUNDÉ 1")
    p.setFont("Helvetica", 6)
    p.setFillColor(C_GOLD_LIGHT)
    p.drawCentredString(width / 2, height - 14 * mm, "FACULTÉ DES SCIENCES • DÉPARTEMENT D'INFORMATIQUE")

    # En-tête Badge (ex: PASS OFFICIEL)
    badge_header = getattr(event, 'badge_header_title', 'PASS OFFICIEL') or "PASS OFFICIEL"
    p.setFont("Helvetica-Bold", 10)
    p.setFillColor(C_BLUE_CYAN)
    p.drawCentredString(width / 2, height - 24 * mm, badge_header.upper())

    # 4. Titre de l'événement (Sous le bandeau)
    event_title = getattr(event, 'title_fr', "Événement Officiel").upper()
    p.setFont("Helvetica-Bold", 10.5)
    p.setFillColor(C_NAVY_DARK)
    
    # Wrapping du titre sur 2 lignes max
    words = event_title.split()
    l1, l2 = "", ""
    max_tw = width - 18 * mm
    for w in words:
        if stringWidth(l1 + " " + w, "Helvetica-Bold", 10.5) < max_tw and not l2:
            l1 += (" " + w if l1 else w)
        else:
            if stringWidth(l2 + " " + w, "Helvetica-Bold", 10.5) < max_tw:
                l2 += (" " + w if l2 else w)
    
    p.drawCentredString(width / 2, height - 37 * mm, l1)
    if l2:
        p.drawCentredString(width / 2, height - 41.5 * mm, l2)
        photo_top_y = height - 48 * mm
    else:
        photo_top_y = height - 45 * mm

    # 5. Cadre Photo Circulaire avec Anneau Doré Double
    photo_diameter = 38 * mm
    photo_x = (width - photo_diameter) / 2
    photo_y = photo_top_y - photo_diameter
    center_x = width / 2
    center_y = photo_y + photo_diameter / 2

    # Double anneau d'or
    p.saveState()
    p.setStrokeColor(C_GOLD_MAIN)
    p.setLineWidth(2.5)
    p.circle(center_x, center_y, photo_diameter / 2 + 1.8 * mm, fill=0, stroke=1)
    p.setStrokeColor(C_BLUE_ROYAL)
    p.setLineWidth(0.8)
    p.circle(center_x, center_y, photo_diameter / 2 + 3.2 * mm, fill=0, stroke=1)

    # Affichage de la photo du participant
    photo_rendered = False
    img_path = participant_data.get('photo_path')
    if img_path and os.path.exists(img_path):
        try:
            circular_img = create_circular_mask(img_path, size=(500, 500))
            if circular_img:
                buf = BytesIO()
                circular_img.save(buf, format='PNG')
                buf.seek(0)
                p.drawImage(ImageReader(buf), photo_x, photo_y, width=photo_diameter, height=photo_diameter, mask='auto', preserveAspectRatio=True)
                photo_rendered = True
        except Exception:
            pass

    if not photo_rendered:
        # Fallback élégant : cercle stylisé avec monogramme
        p.setFillColor(colors.HexColor('#E2E8F0'))
        p.circle(center_x, center_y, photo_diameter / 2, fill=1, stroke=0)
        p.setFillColor(C_BLUE_ROYAL)
        p.setFont("Helvetica-Bold", 18)
        initials = "".join([part[0] for part in participant_data.get('nom_prenom', 'P N').split()[:2]]).upper()
        p.drawCentredString(center_x, center_y - 6 * mm, initials or "VIP")

    p.restoreState()

    # 6. Pastille de Rôle (VIP / PARTICIPANT / ORGANISATEUR)
    role_text = (participant_data.get('role') or getattr(event, 'badge_role_default', 'PARTICIPANT') or "PARTICIPANT").upper()
    pill_w = max(45 * mm, stringWidth(role_text, "Helvetica-Bold", 9) + 16 * mm)
    pill_h = 6.5 * mm
    pill_x = (width - pill_w) / 2
    pill_y = photo_y - 9 * mm

    # Pilule dorée
    p.setFillColor(C_GOLD_MAIN)
    p.roundRect(pill_x, pill_y, pill_w, pill_h, 3 * mm, fill=1, stroke=0)
    p.setFont("Helvetica-Bold", 8.5)
    p.setFillColor(colors.white)
    p.drawCentredString(width / 2, pill_y + 1.8 * mm, role_text)

    # 7. Nom et Promotion du Participant
    name_y = pill_y - 8 * mm
    nom = participant_data.get('nom_prenom', 'Patrice Nguekam Dassi').upper()
    p.setFillColor(C_NAVY_DARK)

    # Auto-scaling du nom pour ne jamais déborder
    name_fs = 14
    while stringWidth(nom, "Helvetica-Bold", name_fs) > (width - 16 * mm) and name_fs > 9:
        name_fs -= 1

    p.setFont("Helvetica-Bold", name_fs)
    p.drawCentredString(width / 2, name_y, nom)

    # Promotion / Niveau
    promo = participant_data.get('promotion')
    if promo:
        p.setFont("Helvetica-Bold", 8.5)
        p.setFillColor(C_TEXT_MUTED)
        p.drawCentredString(width / 2, name_y - 4.5 * mm, f"Promotion : {promo}")

    # 8. Pied du Badge : Signature Président & QR Code
    foot_y = 7 * mm
    
    # Signature à gauche
    sig_path = None
    if getattr(event, 'president_signature', None) and hasattr(event.president_signature, 'path') and os.path.exists(event.president_signature.path):
        sig_path = event.president_signature.path
    else:
        def_sig = os.path.join(settings.BASE_DIR, 'static', 'images', 'signature.png')
        if os.path.exists(def_sig):
            sig_path = def_sig

    p.setFont("Helvetica-Bold", 7)
    p.setFillColor(C_NAVY_DARK)
    p.drawString(10 * mm, foot_y + 19 * mm, "Le Président COMSAS")
    
    p.setStrokeColor(C_GOLD_MAIN)
    p.setLineWidth(0.6)
    p.line(10 * mm, foot_y + 17.5 * mm, 45 * mm, foot_y + 17.5 * mm)

    if sig_path and os.path.exists(sig_path):
        try:
            p.drawImage(ImageReader(sig_path), 10 * mm, foot_y + 2 * mm, width=32 * mm, height=15 * mm, mask='auto', preserveAspectRatio=True)
        except Exception:
            pass

    # QR Code officiel à droite
    qr_size = 19 * mm
    qr_x = width - qr_size - 9 * mm
    qr_y = foot_y + 2 * mm

    uuid_val = participant_data.get('uuid', 'BADGE-2026-COMSAS')
    verify_url = participant_data.get('verify_url') or f"{getattr(settings, 'SITE_URL', 'https://comsas-uy1.com')}/verify/{uuid_val}"

    qr = qrcode.QRCode(box_size=5, border=0)
    qr.add_data(verify_url)
    qr.make(fit=True)
    qr_buf = BytesIO()
    qr.make_image(fill_color="#0A1128", back_color="white").save(qr_buf, 'PNG')
    qr_buf.seek(0)

    p.drawImage(ImageReader(qr_buf), qr_x, qr_y, width=qr_size, height=qr_size)
    p.setFont("Helvetica-Bold", 5)
    p.setFillColor(C_BLUE_ROYAL)
    p.drawCentredString(qr_x + qr_size / 2, qr_y - 2.5 * mm, "SCAN POUR ACCÈS")

    # Logos partenaires additionnels (si existants)
    partners = []
    if getattr(event, 'partner_logo_1', None) and hasattr(event.partner_logo_1, 'path') and os.path.exists(event.partner_logo_1.path):
        partners.append(event.partner_logo_1.path)
    if getattr(event, 'partner_logo_2', None) and hasattr(event.partner_logo_2, 'path') and os.path.exists(event.partner_logo_2.path):
        partners.append(event.partner_logo_2.path)

    for i, plogo in enumerate(partners[:2]):
        try:
            p.drawImage(ImageReader(plogo), 45 * mm + i * 8 * mm, foot_y + 3 * mm, width=7 * mm, height=7 * mm, mask='auto', preserveAspectRatio=True)
        except Exception:
            pass

    # Bordure générale fine du badge
    p.setStrokeColor(C_GOLD_MAIN)
    p.setLineWidth(0.8)
    p.rect(3 * mm, 3 * mm, width - 6 * mm, height - 6 * mm, fill=0, stroke=1)

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer


def generate_badge(registration):
    """
    Génère et sauvegarde le PDF du badge pour une inscription.
    """
    event = registration.event
    if not getattr(event, 'badge_enabled', True):
        return None

    # Recherche photo du participant ou membre
    photo_path = None
    if registration.photo and hasattr(registration.photo, 'path') and os.path.exists(registration.photo.path):
        photo_path = registration.photo.path
    else:
        from main.models import Member
        m = Member.objects.filter(email=registration.email).first()
        if m and m.photo and hasattr(m.photo, 'path') and os.path.exists(m.photo.path):
            photo_path = m.photo.path

    verify_url = f"{getattr(settings, 'SITE_URL', 'https://comsas-uy1.com')}{reverse('ticket_verify', kwargs={'uuid': registration.uuid})}"

    participant_data = {
        'nom_prenom': registration.nom_prenom,
        'promotion': getattr(registration, 'promotion', ''),
        'photo_path': photo_path,
        'uuid': registration.uuid,
        'verify_url': verify_url,
        'role': getattr(event, 'badge_role_default', 'PARTICIPANT'),
    }

    buffer = render_badge_pdf(event, participant_data)

    if registration.badge_pdf:
        registration.badge_pdf.delete(save=False)
    
    registration.badge_pdf.save(f'badge_{registration.uuid}.pdf', File(buffer), save=True)
    return registration.badge_pdf.url


def generate_preview_badge(event):
    """
    Génère un PDF de badge de démonstration pour la prévisualisation dans l'admin.
    """
    participant_data = {
        'nom_prenom': 'Patrice Nguekam Dassi',
        'promotion': 'Master 1 Génie Logiciel',
        'photo_path': None,
        'uuid': 'PREVIEW-BADGE-2026',
        'verify_url': f"{getattr(settings, 'SITE_URL', 'https://comsas-uy1.com')}/verify/preview",
        'role': getattr(event, 'badge_role_default', 'PARTICIPANT'),
    }
    return render_badge_pdf(event, participant_data)
