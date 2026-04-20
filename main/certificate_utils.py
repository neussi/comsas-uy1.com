import qrcode
import os
from io import BytesIO
from django.core.files import File
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, mm
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth
from django.utils import timezone
from django.conf import settings
from django.urls import reverse


def generate_certificate(registration):
    """
    Generates a HIGH-FIDELITY PREMIUM technical certificate.
    Refined with dynamic name scaling for up to 5 names.
    """
    event = registration.event
    
    if not getattr(event, 'certificate_enabled', True):
        return None

    # --- SETUP ---
    buffer = BytesIO()
    # Landscape orientation for a more professional "Award" feel
    page_width, page_height = A4
    page_width, page_height = page_height, page_width 
    p = canvas.Canvas(buffer, pagesize=(page_width, page_height))
    
    # Premium Palette
    ORANGE_MANDAT = colors.Color(243/255, 146/255, 0/255) # #F39200
    TECH_DARK = colors.Color(31/255, 41/255, 55/255) # Deep Gray for text
    GRID_LINE = colors.Color(0, 0, 0, 0.03)

    # 1. Background: High-Contrast White
    p.setFillColor(colors.white)
    p.rect(0, 0, page_width, page_height, fill=1, stroke=0)
    
    # Subtle Technical Grid Layer (Light Gray)
    p.setStrokeColor(GRID_LINE)
    p.setLineWidth(0.5)
    for x in range(0, int(page_width), int(10*mm)): p.line(x, 0, x, page_height)
    for y in range(0, int(page_height), int(10*mm)): p.line(0, y, page_width, y)

    # Decorative Side Accent (Orange)
    p.setFillColor(ORANGE_MANDAT)
    p.rect(0, 0, 8*mm, page_height, fill=1, stroke=0)

    # 2. Main Frame
    p.setStrokeColor(ORANGE_MANDAT)
    p.setLineWidth(1)
    p.rect(12*mm, 10*mm, page_width - 22*mm, page_height - 20*mm, fill=0, stroke=1)
    
    # Corner Indicators
    p.setStrokeColor(TECH_DARK)
    p.setLineWidth(2)
    # Top Left
    p.line(12*mm, page_height - 20*mm, 25*mm, page_height - 20*mm)
    p.line(12*mm, page_height - 20*mm, 12*mm, page_height - 35*mm)
    # Bottom Right
    p.line(page_width - 20*mm, 10*mm, page_width - 10*mm, 10*mm)
    p.line(page_width - 10*mm, 10*mm, page_width - 10*mm, 25*mm)

    # 3. Logos (Top Layer)
    comsas_path = os.path.join(settings.BASE_DIR, 'static/images/comsas.png')
    if os.path.exists(comsas_path):
        p.drawImage(ImageReader(comsas_path), 20*mm, page_height - 35*mm, width=18*mm, height=18*mm, mask='auto', preserveAspectRatio=True)

    # 4. Header Titles
    p.setFillColor(TECH_DARK)
    p.setFont("Helvetica-Bold", 55)
    p.drawCentredString(page_width/2, page_height - 45*mm, "CERTIFICAT")
    
    p.setFillColor(ORANGE_MANDAT)
    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(page_width/2, page_height - 55*mm, "DE PARTICIPATION ET D'EXCELLENCE")

    # 5. Awardee Section (Dynamic Scaling)
    p.setFillColor(colors.gray)
    p.setFont("Helvetica", 16)
    p.drawCentredString(page_width/2, page_height*0.65, "Ce certificat est fièrement décerné à :")
    
    p.setFillColor(ORANGE_MANDAT)
    
    # --- DYNAMIC FONT SCALING ---
    name = registration.nom_prenom.upper()
    max_w = page_width * 0.75
    fs = 48
    while stringWidth(name, "Helvetica-Bold", fs) > max_w and fs > 20:
        fs -= 2
    
    p.setFont("Helvetica-Bold", fs)
    p.drawCentredString(page_width/2, page_height*0.55, name)
    
    # Separator Line
    p.setStrokeColor(TECH_DARK)
    p.setLineWidth(0.5)
    p.line(page_width*0.2, page_height*0.52, page_width*0.8, page_height*0.52)

    # 6. Event Description
    p.setFillColor(TECH_DARK)
    p.setFont("Helvetica", 14)
    desc = event.certificate_main_text or f"pour sa participation remarquable à l'événement \"{event.title_fr}\" organisé par le COMSAS."
    
    # Wrap text
    words = desc.split()
    lines, curr = [], ""
    for w in words:
        if stringWidth(curr + " " + w, "Helvetica", 14) < (page_width - 60*mm): curr += " " + w if curr else w
        else: lines.append(curr); curr = w
    if curr: lines.append(curr)
    
    y_cursor = page_height*0.48
    for line in lines[:4]:
        p.drawCentredString(page_width/2, y_cursor, line)
        y_cursor -= 7*mm

    # 7. Official Signature (CRITICAL POSITIONING: BELOW THE TITLE)
    sig_y_label = 55*mm
    p.setFont("Helvetica-Bold", 12)
    p.setFillColor(TECH_DARK)
    p.drawCentredString(page_width/2, sig_y_label, "Le Président du COMS.A.S")
    
    sig_path = event.president_signature.path if event.president_signature else os.path.join(settings.BASE_DIR, 'static/images/signature.png')
    if os.path.exists(sig_path):
        # ENLARGED STAMP BELOW THE TEXT
        p.drawImage(ImageReader(sig_path), (page_width - 65*mm)/2, sig_y_label - 45*mm, width=65*mm, height=40*mm, mask='auto', preserveAspectRatio=True)

    # 8. Branding & Verification Footer
    # Date & Loc
    p.setFont("Helvetica-Oblique", 11)
    p.setFillColor(colors.gray)
    p.drawString(20*mm, 20*mm, f"Yaoundé, le {timezone.now().strftime('%d %B %Y')}")

    # Partner Logos (Bottom Left Row)
    lp_s = 14*mm
    uy1_path = os.path.join(settings.BASE_DIR, 'static/images/uy1.png')
    final_lp = [uy1_path]
    if event.partner_logo_1: final_lp.append(event.partner_logo_1.path)
    if event.partner_logo_2: final_lp.append(event.partner_logo_2.path)
    
    lp_cursor = 20*mm
    for lp in final_lp[:3]:
        try: p.drawImage(ImageReader(lp), lp_cursor, 28*mm, width=lp_s, height=lp_s, mask='auto', preserveAspectRatio=True)
        except: pass
        lp_cursor += 18*mm

    # QR Code Verification (Repositioned: UP and LEFT)
    qr_s = 28*mm
    qx, qy = page_width - 55*mm, 30*mm 
    verify_url = settings.SITE_URL + reverse('ticket_verify', kwargs={'uuid': registration.uuid})
    qr = qrcode.QRCode(box_size=10, border=1)
    qr.add_data(verify_url)
    qr.make(fit=True)
    qr_buf = BytesIO()
    qr.make_image().save(qr_buf, 'PNG')
    qr_buf.seek(0)
    p.drawImage(ImageReader(qr_buf), qx, qy, width=qr_s, height=qr_s)
    
    p.setFont("Helvetica", 7)
    p.setFillColor(colors.gray)
    p.drawCentredString(qx + qr_s/2, qy - 4*mm, f"ID: {registration.uuid}")
    p.drawCentredString(qx + qr_s/2, qy - 7*mm, "VERIFIER L'AUTHENTICITE")

    p.showPage()
    p.save()
    
    buffer.seek(0)
    if registration.certificate_pdf: registration.certificate_pdf.delete(save=False)
    registration.certificate_pdf.save(f'certificate_{registration.uuid}.pdf', File(buffer), save=True)
    return registration.certificate_pdf.url
