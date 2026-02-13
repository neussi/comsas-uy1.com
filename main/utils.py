import qrcode
from io import BytesIO
from django.core.files import File
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from django.conf import settings
from django.urls import reverse
import os
from django.core.mail import EmailMessage
from reportlab.lib import colors

def generate_member_card(member):
    """Génère une carte de membre PDF (format carte de visite)"""
    buffer = BytesIO()
    # Format carte de visite
    card_width = 3.37 * inch
    card_height = 2.125 * inch
    
    p = canvas.Canvas(buffer, pagesize=(card_width, card_height))
    
    # Background
    p.setFillColor(colors.white)
    p.rect(0, 0, card_width, card_height, fill=1)
    
    # Header
    p.setFillColor(colors.darkblue)
    p.rect(0, card_height - 0.5*inch, card_width, 0.5*inch, fill=1, stroke=0)
    
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(0.2*inch, card_height - 0.35*inch, "COMS.A.S")
    
    # Member Info
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 10)
    p.drawString(0.2*inch, card_height - 0.8*inch, member.nom_prenom[:25] + "..." if len(member.nom_prenom) > 25 else member.nom_prenom)
    
    p.setFont("Helvetica", 8)
    y = card_height - 1.0*inch
    p.drawString(0.2*inch, y, f"Matricule: {member.matricule or 'N/A'}")
    y -= 0.15*inch
    p.drawString(0.2*inch, y, f"Niveau: {member.get_niveau_display() or member.promotion or ''}")
    y -= 0.15*inch
    p.drawString(0.2*inch, y, f"Statut: {member.get_member_type_display()}")
    
    # Footer
    p.setFont("Helvetica", 6)
    p.drawCentredString(card_width/2, 0.1*inch, "Carte de Membre - COMS.A.S UY1")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return buffer

def send_member_card_email(member, pdf_buffer):
    """Envoie la carte de membre par email avec template HTML"""
    from django.template.loader import render_to_string
    from django.core.mail import EmailMultiAlternatives
    
    html_content = render_to_string('emails/member_card_email.html', {
        'member_name': member.nom_prenom,
        'matricule': member.matricule,
        'member_type': member.get_member_type_display(),
        'date_adhesion': member.date_adhesion,
    })
    
    subject = "Votre Carte de Membre COMS.A.S"
    text_content = f"Bonjour {member.nom_prenom},\n\nVeuillez trouver ci-joint votre carte de membre numérique.\n\nCordialement,\nL'équipe COMS.A.S"
    
    email = EmailMultiAlternatives(
        subject,
        text_content,
        settings.EMAIL_HOST_USER,
        [member.email],
    )
    
    email.attach_alternative(html_content, "text/html")
    email.attach(f'carte_membre_{member.matricule}.pdf', pdf_buffer.getvalue(), 'application/pdf')
    email.send(fail_silently=True)


def generate_ticket(registration):
    """
    Generates a premium event ticket (admit one style) with pink/white COMS.A.S branding.
    """
    # 1. Generate QR Code
    verification_url = settings.SITE_URL + reverse('ticket_verify', kwargs={'uuid': registration.uuid})
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=8,
        border=2,
    )
    qr.add_data(verification_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    blob = BytesIO()
    img.save(blob, 'PNG')
    
    # Save QR code image
    registration.qr_code.save(f'qr_{registration.uuid}.png', File(blob), save=False)
    
    # 2. Generate PDF Ticket (Landscape orientation for ticket style)
    buffer = BytesIO()
    # Ticket size: similar to concert ticket (8.5" x 3.5")
    ticket_width = 8.5 * inch
    ticket_height = 3.5 * inch
    
    p = canvas.Canvas(buffer, pagesize=(ticket_width, ticket_height))
    
    # COMS.A.S Brand Colors
    COMSAS_PINK = colors.Color(236/255, 72/255, 153/255)  # Pink/Rose
    DARK_GRAY = colors.Color(0.2, 0.2, 0.2)
    LIGHT_GRAY = colors.Color(0.9, 0.9, 0.9)
    
    # --- Main Ticket Body ---
    # White background
    p.setFillColor(colors.white)
    p.rect(0, 0, ticket_width, ticket_height, fill=1, stroke=0)
    
    # Pink accent bar at top
    p.setFillColor(COMSAS_PINK)
    p.rect(0, ticket_height - 0.4*inch, ticket_width, 0.4*inch, fill=1, stroke=0)
    
    # Pink accent bar at bottom
    p.rect(0, 0, ticket_width, 0.3*inch, fill=1, stroke=0)
    
    # --- Left Stub Section (Tear-off) ---
    stub_width = 1.8*inch
    
    # Vertical dashed line separator
    p.setStrokeColor(LIGHT_GRAY)
    p.setDash(3, 3)
    p.setLineWidth(1)
    p.line(stub_width, 0.3*inch, stub_width, ticket_height - 0.4*inch)
    p.setDash()  # Reset to solid
    
    # Stub content (rotated text)
    p.saveState()
    p.translate(stub_width/2, ticket_height/2)
    p.rotate(90)
    p.setFillColor(DARK_GRAY)
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(0, 0, "ADMIT ONE")
    p.setFont("Helvetica", 10)
    p.drawCentredString(0, -0.25*inch, registration.event.date_event.strftime('%d.%m.%Y'))
    p.restoreState()
    
    # Barcode-style decoration on stub
    p.setFillColor(DARK_GRAY)
    for i in range(15):
        x = 0.2*inch
        y = 0.5*inch + (i * 0.15*inch)
        width = 0.05*inch if i % 3 == 0 else 0.03*inch
        p.rect(x, y, width, 0.1*inch, fill=1, stroke=0)
    
    # --- Main Ticket Content ---
    content_x = stub_width + 0.5*inch
    
    # Logo
    logo_path = os.path.join(settings.BASE_DIR, 'static/images/comsas.png')
    if os.path.exists(logo_path):
        logo_img = ImageReader(logo_path)
        p.drawImage(logo_img, content_x, ticket_height - 1.3*inch, 
                   width=0.8*inch, height=0.8*inch, mask='auto')
    
    # "TICKET" text
    p.setFillColor(DARK_GRAY)
    p.setFont("Helvetica-Bold", 36)
    p.drawString(content_x + 1*inch, ticket_height - 1.1*inch, "TICKET")
    
    # Event title
    p.setFont("Helvetica-Bold", 14)
    p.setFillColor(COMSAS_PINK)
    event_title = registration.event.title_fr
    if len(event_title) > 45:
        event_title = event_title[:42] + "..."
    p.drawString(content_x, ticket_height - 1.6*inch, event_title.upper())
    
    # Event details
    y_pos = ticket_height - 2.0*inch
    p.setFont("Helvetica", 11)
    p.setFillColor(DARK_GRAY)
    
    # Date and time
    date_str = registration.event.date_event.strftime('%d %B %Y')
    time_str = registration.event.date_event.strftime('%H:%M')
    p.drawString(content_x, y_pos, f"DATE: {date_str} • {time_str}")
    
    # Location
    y_pos -= 0.25*inch
    location = registration.event.location
    if len(location) > 50:
        location = location[:47] + "..."
    p.drawString(content_x, y_pos, f"LIEU: {location}")
    
    # Participant
    y_pos -= 0.25*inch
    p.setFont("Helvetica-Bold", 10)
    p.setFillColor(COMSAS_PINK)
    p.drawString(content_x, y_pos, "PARTICIPANT:")
    p.setFont("Helvetica", 10)
    p.setFillColor(DARK_GRAY)
    p.drawString(content_x + 1.2*inch, y_pos, registration.nom_prenom.upper())
    
    # --- Right Section: QR Code ---
    qr_size = 1.4*inch
    qr_x = ticket_width - qr_size - 0.4*inch
    qr_y = (ticket_height - qr_size) / 2
    
    # QR Code background
    p.setFillColor(colors.white)
    p.setStrokeColor(LIGHT_GRAY)
    p.setLineWidth(1)
    p.rect(qr_x - 0.1*inch, qr_y - 0.1*inch, 
           qr_size + 0.2*inch, qr_size + 0.2*inch, 
           fill=1, stroke=1)
    
    # QR Code
    blob.seek(0)
    qr_img = ImageReader(blob)
    p.drawImage(qr_img, qr_x, qr_y, width=qr_size, height=qr_size)
    
    # Scan instruction
    p.setFont("Helvetica", 7)
    p.setFillColor(DARK_GRAY)
    p.drawCentredString(qr_x + qr_size/2, qr_y - 0.25*inch, "SCAN À L'ENTRÉE")
    
    # --- Footer ---
    p.setFont("Helvetica", 7)
    p.setFillColor(colors.white)
    p.drawString(0.3*inch, 0.12*inch, f"ID: {str(registration.uuid)[:13]}")
    p.drawRightString(ticket_width - 0.3*inch, 0.12*inch, 
                     "COMS.A.S • Université de Yaoundé 1")
    
    # Border
    p.setStrokeColor(COMSAS_PINK)
    p.setLineWidth(3)
    p.rect(0, 0, ticket_width, ticket_height, fill=0, stroke=1)
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    registration.ticket_pdf.save(f'ticket_{registration.uuid}.pdf', File(buffer), save=True)
    
    return registration.ticket_pdf.url
