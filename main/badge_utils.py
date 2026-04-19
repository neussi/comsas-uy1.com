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
    """Creates a circular mask for an image"""
    try:
        if not os.path.exists(image_path):
            return None
        img = Image.open(image_path).convert("RGBA")
        img = ImageOps.fit(img, size, centering=(0.5, 0.5))
        
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + size, fill=255)
        
        output = Image.new('RGBA', size, (0, 0, 0, 0))
        output.paste(img, (0, 0), mask=mask)
        return output
    except Exception as e:
        print(f"Error creating circular mask: {e}")
        return None

def generate_badge(registration):
    """
    Generates a CLEAN & PREMIUM event badge (A6 vertical).
    Features: Tech Pattern Background, Strategic Colors, Readable Text.
    Updated: Title overflow fix and Partner Logos.
    """
    event = registration.event
    
    # Check if badges are enabled
    if not getattr(event, 'badge_enabled', True):
        return None

    # --- SETUP ---
    buffer = BytesIO()
    width, height = A6  # 105mm x 148mm
    p = canvas.Canvas(buffer, pagesize=A6)
    
    # Colors
    HEADER_BG = colors.Color(31/255, 41/255, 55/255) # Dark Navy
    WAVE_CYAN = colors.Color(6/255, 182/255, 212/255) # Cyan
    WAVE_RED = colors.Color(239/255, 68/255, 68/255) # Red
    TEXT_BLACK = colors.Color(17/255, 24/255, 39/255)
    TEXT_WHITE = colors.white
    
    # Layout Config
    HEADER_HEIGHT = 65*mm
    PHOTO_SIZE = 36*mm
    PHOTO_CENTER_Y = height - 35*mm
    
    # 1. Backgrounds
    # White Body
    p.setFillColor(colors.white)
    p.rect(0, 0, width, height, fill=1, stroke=0)
    
    # --- TECH PATTERN BACKGROUND ---
    p.saveState()
    p.setFillColor(colors.Color(0.96, 0.96, 0.98)) 
    p.setStrokeColor(colors.Color(0.93, 0.93, 0.95))
    p.setLineWidth(1.5)
    
    p.setFont("Helvetica-Bold", 30)
    p.drawCentredString(width*0.2, height*0.35, "</>")
    p.setFont("Helvetica-Bold", 20)
    p.drawCentredString(width*0.8, height*0.55, "{ }")
    p.restoreState()

    # Dark Header
    p.setFillColor(HEADER_BG)
    header_path = p.beginPath()
    header_path.moveTo(0, height)
    header_path.lineTo(width, height)
    header_path.lineTo(width, height - HEADER_HEIGHT)
    header_path.curveTo(width*0.7, height - HEADER_HEIGHT + 5*mm, width*0.3, height - HEADER_HEIGHT - 5*mm, 0, height - HEADER_HEIGHT)
    header_path.close()
    p.drawPath(header_path, fill=1, stroke=0)
    
    # Accents
    p.saveState()
    p.setFillColor(WAVE_CYAN)
    cyan_path = p.beginPath()
    cyan_path.moveTo(0, height)
    cyan_path.lineTo(30*mm, height)
    cyan_path.curveTo(15*mm, height - 15*mm, 5*mm, height - 20*mm, 0, height - 35*mm)
    cyan_path.close()
    p.drawPath(cyan_path, fill=1, stroke=0)
    p.restoreState()
    
    # Accent 2: Red Edge
    p.saveState()
    p.setFillColor(WAVE_RED)
    red_path = p.beginPath()
    base_y = height - HEADER_HEIGHT
    red_path.moveTo(width, base_y + 15*mm)
    red_path.lineTo(width, base_y - 15*mm)
    red_path.curveTo(width - 15*mm, base_y, width - 25*mm, base_y + 5*mm, width - 20*mm, base_y + 15*mm)
    red_path.close()
    p.drawPath(red_path, fill=1, stroke=0)
    p.restoreState()
    
    # Bottom Footer Curve
    p.saveState()
    p.setFillColor(HEADER_BG)
    footer_path = p.beginPath()
    footer_path.moveTo(0, 0)
    footer_path.lineTo(width, 0)
    footer_path.lineTo(width, 8*mm)
    footer_path.curveTo(width/2, 15*mm, 0, 5*mm, 0, 5*mm)
    footer_path.close()
    p.drawPath(footer_path, fill=1, stroke=0)
    p.restoreState()

    # 3. Logo (Top Left)
    logo_size = 11*mm
    logo_y = height - 16*mm
    logo_x = 8*mm
    
    comsas_logo_path = os.path.join(settings.BASE_DIR, 'static/images/comsas.png')
    if os.path.exists(comsas_logo_path):
        p.saveState()
        p.setFillColor(colors.white)
        p.circle(logo_x + logo_size/2, logo_y + logo_size/2, logo_size/2 + 1.5*mm, fill=1, stroke=0)
        p.drawImage(ImageReader(comsas_logo_path), logo_x, logo_y, width=logo_size, height=logo_size, mask='auto', preserveAspectRatio=True)
        p.restoreState()

    # 4. Photo
    photo_x = (width - PHOTO_SIZE) / 2
    photo_y = height - 52*mm 
    
    # Photo Border
    p.setLineWidth(2.5)
    p.setStrokeColor(colors.white) 
    p.circle(photo_x + PHOTO_SIZE/2, photo_y + PHOTO_SIZE/2, PHOTO_SIZE/2 + 1.2*mm, fill=0, stroke=1)
    
    # Draw Photo
    has_photo = False
    img_path = None
    
    if registration.photo:
        img_path = registration.photo.path
    else:
        from main.models import Member
        linked_member = Member.objects.filter(email=registration.email).first()
        if linked_member and getattr(linked_member, 'photo', None):
            try: img_path = linked_member.photo.path
            except: pass

    if img_path:
        try:
            avatar_img = create_circular_mask(img_path, size=(600, 600))
            if avatar_img:
                img_buffer = BytesIO()
                avatar_img.save(img_buffer, format='PNG')
                img_buffer.seek(0)
                p.drawImage(ImageReader(img_buffer), photo_x, photo_y, width=PHOTO_SIZE, height=PHOTO_SIZE, mask='auto', preserveAspectRatio=True)
                has_photo = True
        except: pass
            
    if not has_photo:
        p.setFillColor(colors.Color(0.9, 0.9, 0.9))
        p.circle(width/2, photo_y + PHOTO_SIZE/2, PHOTO_SIZE/2, fill=1, stroke=0)

    # 5. Header Text
    p.setFont("Helvetica-Bold", 14)
    p.setFillColor(TEXT_WHITE)
    p.drawCentredString(width/2, photo_y - 8*mm, "PARTICIPANT")
    
    # 6. Body Content
    title_y = height - HEADER_HEIGHT - 8*mm
    p.setFont("Helvetica-Bold", 10)
    p.setFillColor(WAVE_CYAN)
    
    event_title = event.title_fr.upper()
    if stringWidth(event_title, "Helvetica-Bold", 10) > width - 15*mm:
        p.setFont("Helvetica-Bold", 8)
        if stringWidth(event_title, "Helvetica-Bold", 8) > width - 15*mm:
            event_title = event_title[:60] + "..."
            
    p.drawCentredString(width/2, title_y, event_title)
    
    # Name
    name_y = title_y - 12*mm
    p.setFont("Helvetica-Bold", 22)
    p.setFillColor(TEXT_BLACK)
    
    name = registration.nom_prenom.upper()
    if stringWidth(name, "Helvetica-Bold", 22) > width - 10*mm:
        p.setFont("Helvetica-Bold", 18)
    if stringWidth(name, "Helvetica-Bold", 18) > width - 10*mm:
        p.setFont("Helvetica-Bold", 14)
        
    p.drawCentredString(width/2, name_y, name)
    
    # Info List
    info_y_cursor = name_y - 12*mm
    p.setFont("Helvetica", 9)
    for line in [f"Promotion: {registration.promotion}", f"Email: {registration.email}"]:
        w = stringWidth(line, "Helvetica", 9)
        start_x = (width - w) / 2
        p.setFillColor(WAVE_RED)
        p.rect(start_x - 4*mm, info_y_cursor, 2*mm, 2*mm, fill=1, stroke=0)
        p.setFillColor(colors.black)
        p.drawString(start_x, info_y_cursor, line)
        info_y_cursor -= 6*mm
        
    # --- Partner Logos on Badge (Dynamic) ---
    p_logos = []
    if event.partner_logo_1: p_logos.append(event.partner_logo_1.path)
    if event.partner_logo_2: p_logos.append(event.partner_logo_2.path)
    if event.partner_logo_3: p_logos.append(event.partner_logo_3.path)
    
    if p_logos:
        p_logo_size = 8*mm
        p_logo_y = 10*mm
        p_spacing = 10*mm
        p_start_x = (width - (len(p_logos)-1)*p_spacing) / 2
        for i, lp in enumerate(p_logos):
            try: p.drawImage(ImageReader(lp), p_start_x + i*p_spacing - p_logo_size/2, p_logo_y, width=p_logo_size, height=p_logo_size, mask='auto', preserveAspectRatio=True)
            except: pass

    # 7. Footer (QR)
    qr_size = 14*mm
    qr_y = 15*mm
    qr_x = 8*mm
    
    qr_url = settings.SITE_URL + reverse('ticket_verify', kwargs={'uuid': registration.uuid})
    qr = qrcode.QRCode(box_size=10, border=1)
    qr.add_data(qr_url)
    qr.make(fit=True)
    qr_blob = BytesIO()
    qr.make_image().save(qr_blob, 'PNG')
    qr_blob.seek(0)
    p.drawImage(ImageReader(qr_blob), qr_x, qr_y, width=qr_size, height=qr_size)
    
    p.setFont("Helvetica", 6)
    p.setFillColor(HEADER_BG)
    p.drawCentredString(qr_x + qr_size/2, qr_y - 3*mm, "SCANNEZ-MOI")

    p.showPage()
    p.save()
    
    buffer.seek(0)
    if registration.badge_pdf: registration.badge_pdf.delete(save=False)
    registration.badge_pdf.save(f'badge_{registration.uuid}.pdf', File(buffer), save=True)
    
    return registration.badge_pdf.url
