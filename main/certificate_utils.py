import qrcode
import os
from io import BytesIO
from django.core.files import File
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth
from django.utils import timezone
from django.conf import settings
from django.urls import reverse


def generate_certificate(registration):
    """
    Generates a premium participation certificate with elegant design.
    Matches the example with decorative borders, dual logos, and QR code.
    Updated to include up to 3 partner logos and the president's signature.
    """
    event = registration.event
    
    # Check if certificates are enabled for this event
    if not event.certificate_enabled:
        return None
    
    # 1. Generate QR Code linking to verification page
    # Using the new verification URL
    verify_url = settings.SITE_URL + reverse('ticket_verify', kwargs={'uuid': registration.uuid})
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=6,
        border=2,
    )
    qr.add_data(verify_url)
    qr.make(fit=True)
    
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_blob = BytesIO()
    qr_img.save(qr_blob, 'PNG')
    qr_blob.seek(0)
    
    # 2. Generate PDF Certificate (A4 Landscape for elegance)
    buffer = BytesIO()
    page_width, page_height = A4
    # Landscape orientation
    page_width, page_height = page_height, page_width
    
    p = canvas.Canvas(buffer, pagesize=(page_width, page_height))
    
    # Premium Colors
    NAVY_BLUE = colors.Color(25/255, 35/255, 75/255)
    GOLD = colors.Color(212/255, 175/255, 55/255)
    CREAM = colors.Color(250/255, 248/255, 245/255)
    TEXT_DARK = colors.Color(40/255, 40/255, 40/255)
    TEXT_LIGHT = colors.Color(100/255, 100/255, 100/255)
    
    # --- Background ---
    p.setFillColor(CREAM)
    p.rect(0, 0, page_width, page_height, fill=1, stroke=0)
    
    # --- Decorative Border ---
    border_margin = 0.4*inch
    # Outer navy border
    p.setStrokeColor(NAVY_BLUE)
    p.setLineWidth(8)
    p.rect(border_margin, border_margin, 
           page_width - 2*border_margin, 
           page_height - 2*border_margin, 
           fill=0, stroke=1)
    
    # Inner gold line
    inner_margin = border_margin + 0.15*inch
    p.setStrokeColor(GOLD)
    p.setLineWidth(1.5)
    p.rect(inner_margin, inner_margin,
           page_width - 2*inner_margin,
           page_height - 2*inner_margin,
           fill=0, stroke=1)
    
    # --- Corner Decorations (Gold ornaments) ---
    def draw_corner_ornament(x, y, rotation=0):
        """Draw decorative corner ornament"""
        p.saveState()
        p.translate(x, y)
        p.rotate(rotation)
        p.setStrokeColor(GOLD)
        p.setLineWidth(2)
        # Curved ornament
        p.arc(-0.3*inch, -0.3*inch, 0.3*inch, 0.3*inch, 0, 90)
        p.arc(-0.2*inch, -0.2*inch, 0.2*inch, 0.2*inch, 0, 90)
        p.restoreState()
    
    # Four corners
    draw_corner_ornament(border_margin + 0.3*inch, page_height - border_margin - 0.3*inch, 0)
    draw_corner_ornament(page_width - border_margin - 0.3*inch, page_height - border_margin - 0.3*inch, 90)
    draw_corner_ornament(page_width - border_margin - 0.3*inch, border_margin + 0.3*inch, 180)
    draw_corner_ornament(border_margin + 0.3*inch, border_margin + 0.3*inch, 270)
    
    # --- HEADER: "ATTESTATION DE PARTICIPATION" ---
    y_pos = page_height - border_margin - 0.9*inch
    p.setFillColor(TEXT_DARK)
    p.setFont("Times-Bold", 30)
    p.drawCentredString(page_width/2, y_pos, "ATTESTATION DE PARTICIPATION")
    
    # --- Event Title (Truncated if too long) ---
    y_pos -= 0.45*inch
    p.setFillColor(TEXT_LIGHT)
    p.setFont("Times-Roman", 18)
    title_text = event.certificate_title or event.title_fr.upper()
    
    # Overflow check for title
    max_title_width = page_width - 2*inch
    if stringWidth(title_text, "Times-Roman", 18) > max_title_width:
        p.setFont("Times-Roman", 14)
        if stringWidth(title_text, "Times-Roman", 14) > max_title_width:
            title_text = title_text[:100] + "..."
            
    p.drawCentredString(page_width/2, y_pos, title_text)
    
    # --- "CE CERTIFICAT EST DÉCERNÉ À:" ---
    y_pos -= 0.5*inch
    p.setFont("Times-Roman", 11)
    p.setFillColor(TEXT_LIGHT)
    p.drawCentredString(page_width/2, y_pos, "CE CERTIFICAT EST DÉCERNÉ À :")
    
    # --- Participant Name ---
    y_pos -= 0.7*inch
    p.setFont("Times-Italic", 38)
    p.setFillColor(TEXT_DARK)
    participant_name = registration.nom_prenom
    p.drawCentredString(page_width/2, y_pos, participant_name)
    
    # --- Description Text ---
    y_pos -= 1.0*inch
    p.setFont("Times-Roman", 11)
    p.setFillColor(TEXT_DARK)
    
    # Full text customization: if certificate_main_text is provided, use it exclusively
    if event.certificate_main_text:
        description = event.certificate_main_text
    else:
        description = event.certificate_description or f"Le computer science association (Club informatique) de l'université de Yaoundé 1 en abrégé COMS.A.S, par la voix de son président certifie que le nommé a participé au {event.title_fr} tenu du {event.date_event.strftime('%d au %d %B %Y')} au centre universitaire des technologies et de l'information de cette université. Ce dernier a démontré un engagement sérieux dans l'apprentissage des technologies et des connaissances abordées. En foi de quoi la présente attestation est établie pour lui valoir ce que de droit."
    
    # Wrap text
    max_width = page_width - 2.5*inch
    words = description.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + " " + word if current_line else word
        if stringWidth(test_line, "Times-Roman", 11) <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    
    # Draw wrapped text
    line_height = 0.28*inch
    for i, line in enumerate(lines[:12]): # Increased line limit
        p.drawCentredString(page_width/2, y_pos - i*line_height, line)
    
    # --- FOOTER SECTION (Single Signature: President Only) ---
    footer_y_base = border_margin + 1.2*inch
    
    # President Signature/Stamp (Centered)
    if event.president_signature:
        sig_width = 1.6*inch
        sig_height = 0.8*inch
        sig_x = page_width/2 - sig_width/2
        sig_y = footer_y_base + 0.3*inch
        p.drawImage(ImageReader(event.president_signature.path), sig_x, sig_y, width=sig_width, height=sig_height, mask='auto', preserveAspectRatio=True)
    
    # Text for President (Centered)
    center_x = page_width/2
    p.setFont("Times-Roman", 10)
    p.setFillColor(TEXT_DARK)
    p.drawCentredString(center_x, footer_y_base + 0.95*inch, f"Fait à Yaoundé, le {timezone.now().strftime('%d/%m/%Y')}")
    
    p.setFont("Times-Bold", 12)
    p.drawCentredString(center_x, footer_y_base + 0.25*inch, event.certificate_president_name)
    
    p.setFont("Times-Roman", 10)
    p.setFillColor(TEXT_LIGHT)
    p.drawCentredString(center_x, footer_y_base, event.certificate_president_title)
    
    # --- LOGOS AT BOTTOM (Dynamic Partners Layout) ---
    logo_y = border_margin + 0.45*inch
    logo_size = 1.0*inch # Slightly smaller to fit more
    
    # Collect all existing logos
    logos = []
    # Always include COMSAS
    comsas_path = os.path.join(settings.BASE_DIR, 'static/images/comsas.png')
    if os.path.exists(comsas_path):
        logos.append(comsas_path)
    
    # Add UY1
    uy1_path = os.path.join(settings.BASE_DIR, 'static/images/uy1.png')
    if os.path.exists(uy1_path):
        logos.append(uy1_path)
        
    # Add Partner Logos
    if event.partner_logo_1: logos.append(event.partner_logo_1.path)
    if event.partner_logo_2: logos.append(event.partner_logo_2.path)
    if event.partner_logo_3: logos.append(event.partner_logo_3.path)
    
    # Deduplicate and limit to 5 logos total (COMSAS + UY1 + 3 Partners)
    unique_logos = []
    for l in logos:
        if l not in unique_logos: unique_logos.append(l)
    
    n_logos = len(unique_logos)
    spacing = 1.2*inch
    start_x = (page_width - (n_logos - 1) * spacing) / 2
    
    for i, logo_path in enumerate(unique_logos):
        lx = start_x + (i * spacing)
        try:
            img = ImageReader(logo_path)
            p.drawImage(img, lx - logo_size/2, logo_y, width=logo_size, height=logo_size, mask='auto', preserveAspectRatio=True)
        except:
            pass
            
    # --- QR Code ---
    qr_size = 0.65*inch
    qr_x = page_width - border_margin - qr_size - 0.4*inch
    qr_y = border_margin + 0.6*inch
    
    qr_reader = ImageReader(qr_blob)
    p.drawImage(qr_reader, qr_x, qr_y, width=qr_size, height=qr_size)
    
    # QR label
    p.setFont("Helvetica", 6)
    p.setFillColor(TEXT_LIGHT)
    p.drawCentredString(qr_x + qr_size/2, qr_y - 0.12*inch, "Vérifier l'authenticité")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    # Cleanup old file if exists
    if registration.certificate_pdf:
        registration.certificate_pdf.delete(save=False)
    registration.certificate_pdf.save(f'certificate_{registration.uuid}.pdf', File(buffer), save=True)
    
    return registration.certificate_pdf.url
