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
    
    # --- TECH PATTERN BACKGROUND (Subtle Watermarks) ---
    p.saveState()
    # Very light grey
    p.setFillColor(colors.Color(0.96, 0.96, 0.98)) 
    p.setStrokeColor(colors.Color(0.93, 0.93, 0.95))
    p.setLineWidth(1.5)
    
    # Symbol 1: Code Tags </>
    p.setFont("Helvetica-Bold", 30)
    p.drawCentredString(width*0.2, height*0.35, "</>")
    
    # Symbol 2: Curly Braces { }
    p.setFont("Helvetica-Bold", 20)
    p.drawCentredString(width*0.8, height*0.55, "{ }")
    
    # Symbol 3: Binary/Circuit Circles (Top Right area)
    for i in range(5):
        cx, cy = width * (0.6 + i*0.2), height * 0.25
        # Don't draw if outside
    
    # Symbol 4: Network Nodes (Triangular connection) - Bottom Rightish
    nx, ny = width*0.8, height*0.2
    p.circle(nx, ny, 2*mm, fill=1, stroke=0)
    p.circle(nx-10*mm, ny+8*mm, 2*mm, fill=1, stroke=0)
    p.circle(nx-8*mm, ny-8*mm, 2*mm, fill=1, stroke=0)
    p.setLineWidth(0.8)
    p.line(nx, ny, nx-10*mm, ny+8*mm)
    p.line(nx, ny, nx-8*mm, ny-8*mm)
    
    p.restoreState()

    # Dark Header (Top 40%)
    p.setFillColor(HEADER_BG)
    header_path = p.beginPath()
    header_path.moveTo(0, height)
    header_path.lineTo(width, height)
    header_path.lineTo(width, height - HEADER_HEIGHT)
    header_path.curveTo(width*0.7, height - HEADER_HEIGHT + 5*mm, width*0.3, height - HEADER_HEIGHT - 5*mm, 0, height - HEADER_HEIGHT)
    header_path.close()
    p.drawPath(header_path, fill=1, stroke=0)
    
    # 2. Strategic "Bordure" Accents
    # Accent 1: Cyan Corner (Top Left)
    p.saveState()
    p.setFillColor(WAVE_CYAN)
    cyan_path = p.beginPath()
    cyan_path.moveTo(0, height)
    cyan_path.lineTo(30*mm, height)
    cyan_path.curveTo(15*mm, height - 15*mm, 5*mm, height - 20*mm, 0, height - 35*mm)
    cyan_path.close()
    p.drawPath(cyan_path, fill=1, stroke=0)
    p.restoreState()
    
    # Accent 2: Red Edge (Right Side)
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
    
    # Accent 3: Bottom Footer Curve
    p.saveState()
    p.setFillColor(HEADER_BG)
    footer_path = p.beginPath()
    footer_path.moveTo(0, 0)
    footer_path.lineTo(width, 0)
    footer_path.lineTo(width, 8*mm)
    footer_path.curveTo(width/2, 15*mm, 0, 5*mm, 0, 5*mm)
    footer_path.close()
    p.drawPath(footer_path, fill=1, stroke=0)
    
    # Colored line at bottom
    p.setStrokeColor(WAVE_CYAN)
    p.setLineWidth(2)
    p.line(0, 0, width, 0)
    p.restoreState()

    # 3. Logo (Top Left)
    logo_size = 13*mm
    logo_y = height - 18*mm
    logo_x = 10*mm # Left aligned
    
    comsas_logo_path = os.path.join(settings.BASE_DIR, 'static/images/comsas.png')
    if os.path.exists(comsas_logo_path):
        p.setFillColor(colors.white)
        # Circle bg
        p.circle(logo_x + logo_size/2, logo_y + logo_size/2, logo_size/2 + 2*mm, fill=1, stroke=0)
        p.drawImage(ImageReader(comsas_logo_path), logo_x, logo_y, width=logo_size, height=logo_size, mask='auto', preserveAspectRatio=True)

    # 4. Photo (Centered in Header)
    photo_x = (width - PHOTO_SIZE) / 2
    photo_y = height - 55*mm 
    
    # Photo Border
    p.setLineWidth(3)
    p.setStrokeColor(colors.white) 
    p.circle(photo_x + PHOTO_SIZE/2, photo_y + PHOTO_SIZE/2, PHOTO_SIZE/2 + 1.5*mm, fill=0, stroke=1)
    
    # Tech Rings
    p.setLineWidth(1)
    p.setStrokeColor(WAVE_CYAN)
    p.arc(photo_x - 2*mm, photo_y - 2*mm, photo_x + PHOTO_SIZE + 2*mm, photo_y + PHOTO_SIZE + 2*mm, 45, 135)
    p.setStrokeColor(WAVE_RED)
    p.arc(photo_x - 2*mm, photo_y - 2*mm, photo_x + PHOTO_SIZE + 2*mm, photo_y + PHOTO_SIZE + 2*mm, 225, 315)

    # Draw Photo
    has_photo = False
    if registration.photo:
        try:
            avatar_img = create_circular_mask(registration.photo.path, size=(600, 600))
            if avatar_img:
                img_buffer = BytesIO()
                avatar_img.save(img_buffer, format='PNG')
                img_buffer.seek(0)
                p.drawImage(ImageReader(img_buffer), photo_x, photo_y, width=PHOTO_SIZE, height=PHOTO_SIZE, mask='auto', preserveAspectRatio=True)
                has_photo = True
        except Exception as e:
            print(f"Photo error: {e}")
            
    if not has_photo:
        # Default Avatar
        p.setFillColor(colors.Color(0.9, 0.9, 0.9))
        p.circle(width/2, photo_y + PHOTO_SIZE/2, PHOTO_SIZE/2, fill=1, stroke=0)
        p.setFillColor(HEADER_BG)
        p.circle(width/2, photo_y + PHOTO_SIZE*0.65, 7*mm, fill=1, stroke=0)
        p.ellipse(width/2 - 12*mm, photo_y, width/2 + 12*mm, photo_y + 14*mm, fill=1, stroke=0)

    # 5. Header Text: "PARTICIPANT" ONLY (In Dark Header)
    text_y_cursor = photo_y - 8*mm
    p.setFont("Helvetica-Bold", 14)
    p.setFillColor(TEXT_WHITE)
    p.drawCentredString(width/2, text_y_cursor, "PARTICIPANT")
    
    # 6. Body Content (White Section)
    
    # Event Title - MOVED DOWN to White Section for Visibility
    # Position: Just below the header curve (~height - HEADER_HEIGHT - 10mm)
    title_y = height - HEADER_HEIGHT - 8*mm
    p.setFont("Helvetica-Bold", 10)
    p.setFillColor(WAVE_CYAN) # Cyan text on White bg is readable
    p.drawCentredString(width/2, title_y, event.title_fr[:50].upper())
    
    # Name - Moved down further
    name_y = title_y - 12*mm
    p.setFont("Helvetica-Bold", 24)
    p.setFillColor(TEXT_BLACK)
    
    name = registration.nom_prenom.upper()
    if stringWidth(name, "Helvetica-Bold", 24) > width - 10*mm:
        p.setFont("Helvetica-Bold", 20)
    if stringWidth(name, "Helvetica-Bold", 20) > width - 10*mm:
        p.setFont("Helvetica-Bold", 16)
        
    p.drawCentredString(width/2, name_y, name)
    
    # Info List
    info_y_cursor = name_y - 15*mm
    p.setFont("Helvetica", 11)
    
    info_lines = []
    if registration.promotion:
        info_lines.append(f"Promotion: {registration.promotion}")
    if registration.email:
        info_lines.append(f"Email: {registration.email}")
        
    for line in info_lines:
        w = stringWidth(line, "Helvetica", 11)
        start_x = (width - w) / 2
        
        # Red Square Bullet
        p.setFillColor(WAVE_RED)
        p.rect(start_x - 5*mm, info_y_cursor, 2.5*mm, 2.5*mm, fill=1, stroke=0)
        
        # Text
        p.setFillColor(colors.black)
        p.drawString(start_x, info_y_cursor, line)
        
        info_y_cursor -= 7*mm
        
    # 7. Footer (QR & Barcode)
    qr_size = 15*mm
    qr_y = 15*mm
    qr_x = 10*mm
    
    # QR Code
    qr_url = settings.SITE_URL + reverse('ticket_verify', kwargs={'uuid': registration.uuid})
    qr = qrcode.QRCode(box_size=10, border=1)
    qr.add_data(qr_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    qr_blob = BytesIO()
    qr_img.save(qr_blob, 'PNG')
    qr_blob.seek(0)
    p.drawImage(ImageReader(qr_blob), qr_x, qr_y, width=qr_size, height=qr_size)
    
    # Tech Barcode
    bar_x = width - 15*mm - 35*mm
    bar_y = qr_y + 2*mm
    bar_h = 18*mm
    p.setStrokeColor(TEXT_BLACK)
    for i in range(30):
        w = 0.5 if i % 3 == 0 else 1.2
        p.setLineWidth(w)
        p.line(bar_x + i*1.2*mm, bar_y, bar_x + i*1.2*mm, bar_y + bar_h)

    # Scan Text
    p.setFont("Helvetica", 7)
    p.setFillColor(HEADER_BG)
    p.drawCentredString(qr_x + qr_size/2, qr_y - 3*mm, "SCANNEZ-MOI")

    p.showPage()
    p.save()
    
    buffer.seek(0)
    filename = f'badge_{registration.uuid}.pdf'
    if registration.badge_pdf:
        registration.badge_pdf.delete(save=False)
    registration.badge_pdf.save(filename, File(buffer), save=True)
    
    return registration.badge_pdf.url
