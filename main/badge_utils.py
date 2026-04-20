import qrcode
import os
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

def create_circular_mask(image_path, size=(400, 400)):
    """Creates a premium circular mask with high fidelity"""
    try:
        if not os.path.exists(image_path): return None
        img = Image.open(image_path).convert("RGBA")
        img = ImageOps.fit(img, size, centering=(0.5, 0.5))
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + size, fill=255)
        output = Image.new('RGBA', size, (0, 0, 0, 0))
        output.paste(img, (0, 0), mask=mask)
        return output
    except: return None

def generate_badge(registration):
    """
    ULTIMATE PREMIUM TECH BADGE (REFINED).
    Fixed spacing, reduced photo size, and dynamic name scaling.
    """
    event = registration.event
    if not getattr(event, 'badge_enabled', True): return None

    # --- SETUP ---
    buffer = BytesIO()
    width, height = A6
    p = canvas.Canvas(buffer, pagesize=A6)
    
    # Premium Palette
    ORANGE_MANDAT = colors.Color(243/255, 146/255, 0/255)
    TECH_DARK = colors.Color(17/255, 24/255, 39/255)
    OFF_WHITE = colors.Color(0.98, 0.98, 0.98)

    # 1. Background: Dual-Tone High Fidelity
    p.setFillColor(OFF_WHITE)
    p.rect(0, 0, width, height, fill=1, stroke=0)
    
    # Vertical Brand Sidebar (Left)
    sidebar_w = 12*mm
    p.setFillColor(TECH_DARK)
    p.rect(0, 0, sidebar_w, height, fill=1, stroke=0)
    
    # Accent Line (Orange)
    p.setFillColor(ORANGE_MANDAT)
    p.rect(sidebar_w - 1*mm, 0, 1*mm, height, fill=1, stroke=0)

    # 2. Tech Watermark Pattern (Circuit Nodes)
    p.setStrokeColor(colors.Color(0, 0, 0, 0.05))
    p.setLineWidth(0.3)
    p.circle(width*0.8, height*0.8, 15*mm, fill=0, stroke=1)
    p.circle(width*0.8, height*0.8, 12*mm, fill=0, stroke=1)
    p.line(width*0.8, height*0.8, width, height)
    
    # 3. Vertical Branding (Sidebar)
    p.saveState()
    p.translate(sidebar_w/2 + 1*mm, height/2)
    p.rotate(90)
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 10)
    p.drawCentredString(0, 0, "COMPUTER SCIENCE ASSOCIATION")
    p.restoreState()

    # 4. Header Section (Top Right - Refined Spacing)
    comsas_path = os.path.join(settings.BASE_DIR, 'static/images/comsas.png')
    if os.path.exists(comsas_path):
        # Slightly more breathing room from top/right
        p.drawImage(ImageReader(comsas_path), width - 25*mm, height - 25*mm, width=16*mm, height=16*mm, mask='auto', preserveAspectRatio=True)

    header_x = sidebar_w + 6*mm
    p.setFillColor(TECH_DARK)
    p.setFont("Helvetica-Bold", 14)
    # Shifting text down significantly to clear the logo (which is at height - 25mm to height - 9mm)
    p.drawString(header_x, height - 20*mm, "PASS OFFICIEL") 
    
    p.setFillColor(ORANGE_MANDAT)
    p.setFont("Helvetica-Bold", 10)
    # --- MULTI-LINE TITLE WRAPPING ---
    title = event.title_fr.upper()
    max_title_w = (width - sidebar_w - 30*mm) # Stay clear of logo area
    words = title.split()
    t_lines, curr_t = [], ""
    for w in words:
        if stringWidth(curr_t + " " + w, "Helvetica-Bold", 10) < max_title_w:
            curr_t += " " + w if curr_t else w
        else:
            t_lines.append(curr_t)
            curr_t = w
    if curr_t: t_lines.append(curr_t)
    
    t_y = height - 25*mm
    for t_line in t_lines[:3]: # Allow up to 3 lines
        p.drawString(header_x, t_y, t_line)
        t_y -= 4*mm

    # 5. Profile Photo (Reduced to 45mm for better spacing)
    photo_size = 45*mm
    px, py = sidebar_w + (width - sidebar_w - photo_size)/2, height - 82*mm
    
    # Premium Ring
    p.setStrokeColor(ORANGE_MANDAT)
    p.setLineWidth(2.5)
    p.circle(px + photo_size/2, py + photo_size/2, photo_size/2 + 2*mm, fill=0, stroke=1)
    
    img_path = registration.photo.path if registration.photo else None
    if not img_path:
        from main.models import Member
        m = Member.objects.filter(email=registration.email).first()
        if m and m.photo: img_path = m.photo.path
        
    if img_path:
        try:
            avatar = create_circular_mask(img_path, size=(600, 600))
            if avatar:
                img_buf = BytesIO()
                avatar.save(img_buf, format='PNG')
                img_buf.seek(0)
                p.drawImage(ImageReader(img_buf), px, py, width=photo_size, height=photo_size, mask='auto', preserveAspectRatio=True)
        except: pass

    # 6. Participant Identity (Dynamic Scaling)
    y_label = py - 12*mm # Spacing from photo
    p.setFillColor(ORANGE_MANDAT)
    p.setFont("Helvetica-Bold", 11)
    p.drawCentredString(sidebar_w + (width-sidebar_w)/2, y_label, "PARTICIPANT")
    
    y_name = y_label - 10*mm
    p.setFillColor(TECH_DARK)
    
    # --- DYNAMIC FONT SCALING ---
    name = registration.nom_prenom.upper()
    max_w = (width - sidebar_w - 10*mm)
    initial_fs = 26
    while stringWidth(name, "Helvetica-Bold", initial_fs) > max_w and initial_fs > 12:
        initial_fs -= 2
    
    p.setFont("Helvetica-Bold", initial_fs)
    p.drawCentredString(sidebar_w + (width-sidebar_w)/2, y_name, name)
    
    y_prom = y_name - 7*mm
    p.setFont("Helvetica", 10)
    p.setFillColor(colors.gray)
    p.drawCentredString(sidebar_w + (width-sidebar_w)/2, y_prom, f"Prom: {registration.promotion}")

    # 7. Officiality Section (Balanced Footer)
    sig_y = 15*mm
    p.setFont("Helvetica-Bold", 8)
    p.setFillColor(TECH_DARK)
    p.drawString(sidebar_w + 6*mm, sig_y + 10*mm, "Le Président du COMS.A.S")
    
    sig_path = event.president_signature.path if event.president_signature else os.path.join(settings.BASE_DIR, 'static/images/signature.png')
    if os.path.exists(sig_path):
        # Slightly enlarged signature to look "Official" but not crowded
        p.drawImage(ImageReader(sig_path), sidebar_w + 6*mm, sig_y - 12*mm, width=38*mm, height=22*mm, mask='auto', preserveAspectRatio=True)

    # 8. QR Code & Identity
    qr_s = 20*mm
    qx, qy = width - qr_s - 6*mm, 8*mm
    qr_url = settings.SITE_URL + reverse('ticket_verify', kwargs={'uuid': registration.uuid})
    qr = qrcode.QRCode(box_size=10, border=1); qr.add_data(qr_url); qr.make(fit=True)
    qb = BytesIO(); qr.make_image().save(qb, 'PNG'); qb.seek(0)
    p.drawImage(ImageReader(qb), qx, qy, width=qr_s, height=qr_s)
    
    # Partner Logos (Small aligned bottom)
    uy1_path = os.path.join(settings.BASE_DIR, 'static/images/uy1.png')
    lp = [uy1_path]
    if event.partner_logo_1: lp.append(event.partner_logo_1.path)
    if event.partner_logo_2: lp.append(event.partner_logo_2.path)
    
    for i, lpath in enumerate(lp[:3]):
        try: p.drawImage(ImageReader(lpath), width - 38*mm - i*11*mm, 8*mm, width=8*mm, height=8*mm, mask='auto', preserveAspectRatio=True)
        except: pass

    p.showPage()
    p.save()
    buffer.seek(0)
    if registration.badge_pdf: registration.badge_pdf.delete(save=False)
    registration.badge_pdf.save(f'badge_{registration.uuid}.pdf', File(buffer), save=True)
    return registration.badge_pdf.url
