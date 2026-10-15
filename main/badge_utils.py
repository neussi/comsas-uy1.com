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


def get_trimmed_signature_reader(image_path):
    """Rogne les marges transparentes de la signature/cachet pour un rendu grand, net et parfaitement positionné"""
    try:
        if not image_path or not os.path.exists(image_path):
            return None
        im = Image.open(image_path)
        bbox = im.getbbox()
        if bbox:
            im = im.crop(bbox)
        buf = BytesIO()
        im.save(buf, format='PNG')
        buf.seek(0)
        return ImageReader(buf)
    except Exception:
        return ImageReader(image_path) if image_path and os.path.exists(image_path) else None


def render_badge_pdf(event, participant_data):
    """
    Rendu du Badge A6 Portrait officiel ultra-soigné.
    Reprend la structure professionnelle acclamée :
    - Bandeau latéral gauche sombre avec typographie verticale
    - Logos officiels (UY1 et COMSAS)
    - Titre percutant et cadre photo à anneau doré
    - Rôle et nom dynamiquement calibrés
    - Signature officielle posée SUR la ligne et QR Code haute fidélité
    """
    buffer = BytesIO()
    width, height = A6  # 105mm x 148mm
    p = canvas.Canvas(buffer, pagesize=A6)

    # Couleurs du Badge Officiel COMSAS
    C_SIDEBAR_DARK = colors.HexColor('#0F172A')
    C_ACCENT_ORANGE = colors.HexColor('#F39200')
    C_TEXT_DARK = colors.HexColor('#0F172A')
    C_TEXT_MUTED = colors.HexColor('#64748B')
    C_BORDER_LIGHT = colors.HexColor('#E2E8F0')

    # 1. Fond blanc pur
    p.setFillColor(colors.white)
    p.rect(0, 0, width, height, fill=1, stroke=0)

    # 2. Barre latérale gauche iconique (Spine Brandée)
    sidebar_w = 12 * mm
    p.setFillColor(C_SIDEBAR_DARK)
    p.rect(0, 0, sidebar_w, height, fill=1, stroke=0)

    # Liseré vertical orange/or
    accent_w = 1.2 * mm
    p.setFillColor(C_ACCENT_ORANGE)
    p.rect(sidebar_w - accent_w, 0, accent_w, height, fill=1, stroke=0)

    # Texte vertical pivoté à 90° dans la barre latérale
    p.saveState()
    p.translate(sidebar_w / 2 - 0.5 * mm, height / 2)
    p.rotate(90)
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 8.5)
    p.drawCentredString(0, 0, "COMPUTER SCIENCE ASSOCIATION • UY1")
    p.restoreState()

    # Zone de contenu principal
    content_start_x = sidebar_w + 5 * mm
    content_w = width - content_start_x - 5 * mm
    center_content_x = content_start_x + content_w / 2

    # 3. En-tête : Logos UY1 (Premier) & COMSAS
    uy1_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'uy1.png')
    comsas_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'comsas.png')
    
    logo_size = 13.5 * mm
    top_logo_y = height - 19 * mm

    # Logo COMSAS à droite
    if os.path.exists(comsas_path):
        try:
            p.drawImage(ImageReader(comsas_path), width - 6 * mm - logo_size, top_logo_y, width=logo_size, height=logo_size, mask='auto', preserveAspectRatio=True)
        except Exception:
            pass

    # Logo UY1 à gauche du logo COMSAS
    if os.path.exists(uy1_path):
        try:
            p.drawImage(ImageReader(uy1_path), width - 6 * mm - logo_size * 2 - 2 * mm, top_logo_y, width=logo_size, height=logo_size, mask='auto', preserveAspectRatio=True)
        except Exception:
            pass

    # En-tête "PASS OFFICIEL"
    badge_header = (getattr(event, 'badge_header_title', '') or "PASS OFFICIEL").upper()
    p.setFont("Helvetica-Bold", 12.5)
    p.setFillColor(C_TEXT_DARK)
    p.drawString(content_start_x, height - 12 * mm, badge_header)

    # 4. Titre de l'événement (En orange/ambre, élégant et lisible)
    event_title = getattr(event, 'title_fr', "Événement Officiel").upper()
    p.setFont("Helvetica-Bold", 8.5)
    p.setFillColor(C_ACCENT_ORANGE)

    words = event_title.split()
    t_lines, cur_line = [], ""
    max_title_w = content_w - (logo_size * 2 + 5 * mm)  # Dégagé des logos
    
    for w in words:
        if stringWidth(cur_line + " " + w, "Helvetica-Bold", 8.5) < max_title_w:
            cur_line += (" " + w if cur_line else w)
        else:
            t_lines.append(cur_line)
            cur_line = w
    if cur_line:
        t_lines.append(cur_line)

    title_y = height - 17.5 * mm
    for line in t_lines[:3]:
        p.drawString(content_start_x, title_y, line)
        title_y -= 3.8 * mm

    # 5. Cadre Photo Circulaire au centre
    photo_diameter = 44 * mm
    photo_x = center_content_x - photo_diameter / 2
    photo_y = height - 76 * mm

    # Double anneau d'or élégant
    p.saveState()
    p.setStrokeColor(C_ACCENT_ORANGE)
    p.setLineWidth(2.2)
    p.circle(center_content_x, photo_y + photo_diameter / 2, photo_diameter / 2 + 1.5 * mm, fill=0, stroke=1)
    p.restoreState()

    # Rendu de la photo
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
        # Silhouette neutre élégante
        p.saveState()
        p.setFillColor(colors.HexColor('#F1F5F9'))
        p.circle(center_content_x, photo_y + photo_diameter / 2, photo_diameter / 2, fill=1, stroke=0)
        
        # Icône tête et buste vectorielle stylisée
        p.setFillColor(colors.HexColor('#CBD5E1'))
        # Tête
        p.circle(center_content_x, photo_y + photo_diameter / 2 + 5 * mm, 7 * mm, fill=1, stroke=0)
        # Épaules
        shoulder = p.beginPath()
        shoulder.arc(photo_x + 5 * mm, photo_y, photo_x + photo_diameter - 5 * mm, photo_y + 24 * mm, 0, 180)
        shoulder.close()
        p.drawPath(shoulder, fill=1, stroke=0)
        p.restoreState()

    # 6. Rôle du Participant (Badge / Pillule dorée)
    role_text = (participant_data.get('role') or getattr(event, 'badge_role_default', 'PARTICIPANT') or "PARTICIPANT").upper()
    p.setFont("Helvetica-Bold", 10.5)
    p.setFillColor(C_ACCENT_ORANGE)
    p.drawCentredString(center_content_x, photo_y - 8 * mm, role_text)

    # 7. Nom et Prénom du Participant
    nom = participant_data.get('nom_prenom', 'Patrice Nguekam Dassi').upper()
    name_fs = 14.5
    while stringWidth(nom, "Helvetica-Bold", name_fs) > (content_w - 4 * mm) and name_fs > 9:
        name_fs -= 0.5

    p.setFont("Helvetica-Bold", name_fs)
    p.setFillColor(C_TEXT_DARK)
    p.drawCentredString(center_content_x, photo_y - 15 * mm, nom)

    # Promotion / Affiliation
    promo = participant_data.get('promotion')
    if promo:
        p.setFont("Helvetica", 9)
        p.setFillColor(C_TEXT_MUTED)
        p.drawCentredString(center_content_x, photo_y - 20.5 * mm, f"Prom : {promo}")

    # 8. Pied du Badge : Signature à gauche, QR Code à droite
    sig_line_y = 22 * mm
    sig_line_x = content_start_x
    sig_line_w = 38 * mm

    # Titre du signataire AU-DESSUS du trait
    pres_title = getattr(event, 'certificate_president_title', 'Le Président du COMS.A.S') or "Le Président du COMS.A.S"
    p.setFont("Helvetica-Bold", 8)
    p.setFillColor(C_TEXT_DARK)
    p.drawString(sig_line_x, sig_line_y + 2.8 * mm, pres_title)

    # Ligne de séparation
    p.setStrokeColor(C_BORDER_LIGHT)
    p.setLineWidth(0.8)
    p.line(sig_line_x, sig_line_y, sig_line_x + sig_line_w, sig_line_y)

    # Image du cachet et signature : EN DESSOUS du trait et agrandie (contient déjà signature + nom nominatif)
    sig_path = None
    if getattr(event, 'president_signature', None) and hasattr(event.president_signature, 'path') and os.path.exists(event.president_signature.path):
        sig_path = event.president_signature.path
    else:
        def_sig = os.path.join(settings.BASE_DIR, 'static', 'images', 'signature.png')
        if os.path.exists(def_sig):
            sig_path = def_sig

    if sig_path and os.path.exists(sig_path):
        try:
            reader = get_trimmed_signature_reader(sig_path)
            if reader:
                p.drawImage(reader, sig_line_x, sig_line_y - 18.5 * mm, width=36 * mm, height=17.5 * mm, mask='auto', preserveAspectRatio=True)
        except Exception:
            pass
    # Pas de nom texte en dessous car le cachet contient déjà le nominatif complet

    # QR Code haute définition à droite
    qr_size = 22 * mm
    qr_x = width - qr_size - 6 * mm
    qr_y = 9 * mm

    uuid_val = participant_data.get('uuid', 'BADGE-2026-COMSAS')
    verify_url = participant_data.get('verify_url') or f"{getattr(settings, 'SITE_URL', 'https://comsas-uy1.com')}/verify/{uuid_val}"

    qr = qrcode.QRCode(box_size=6, border=0)
    qr.add_data(verify_url)
    qr.make(fit=True)
    qr_buf = BytesIO()
    qr.make_image(fill_color="#0F172A", back_color="white").save(qr_buf, 'PNG')
    qr_buf.seek(0)

    p.drawImage(ImageReader(qr_buf), qr_x, qr_y, width=qr_size, height=qr_size)
    p.setFont("Helvetica-Bold", 5.5)
    p.setFillColor(C_ACCENT_ORANGE)
    p.drawCentredString(qr_x + qr_size / 2, qr_y - 3.5 * mm, "SCAN POUR ACCÈS")

    # Logos partenaires additionnels (si existants)
    partners = []
    if getattr(event, 'partner_logo_1', None) and hasattr(event.partner_logo_1, 'path') and os.path.exists(event.partner_logo_1.path):
        partners.append(event.partner_logo_1.path)
    if getattr(event, 'partner_logo_2', None) and hasattr(event.partner_logo_2, 'path') and os.path.exists(event.partner_logo_2.path):
        partners.append(event.partner_logo_2.path)

    for i, plogo in enumerate(partners[:2]):
        try:
            p.drawImage(ImageReader(plogo), sig_line_x + sig_line_w + 3 * mm + i * 8 * mm, 12 * mm, width=7 * mm, height=7 * mm, mask='auto', preserveAspectRatio=True)
        except Exception:
            pass

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer


def generate_badge(registration):
    """Génère et sauvegarde le badge pour une inscription"""
    event = registration.event
    if not getattr(event, 'badge_enabled', True):
        return None

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
    """Génère un badge de démonstration pour la prévisualisation dans l'admin"""
    participant_data = {
        'nom_prenom': 'Patrice Nguekam Dassi',
        'promotion': 'Master 2 - Sécurité Informatique',
        'photo_path': None,
        'uuid': 'PREVIEW-BADGE-2026',
        'verify_url': f"{getattr(settings, 'SITE_URL', 'https://comsas-uy1.com')}/verify/preview",
        'role': getattr(event, 'badge_role_default', 'PARTICIPANT'),
    }
    return render_badge_pdf(event, participant_data)
