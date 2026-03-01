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
    """
    Génère une carte de membre professionnelle au format PDF.
    Taille standard CR80 (85.6mm x 53.98mm).
    """
    # We need mm from reportlab.lib.units
    from reportlab.lib.units import mm
    
    # Dimensions carte de crédit standard
    width, height = 85.6 * mm, 54 * mm
    buffer = BytesIO()
    
    c = canvas.Canvas(buffer, pagesize=(width, height))
    
    # --- FOND & DESIGN ---
    # Fond blanc
    c.setFillColorRGB(1, 1, 1)
    c.rect(0, 0, width, height, fill=1, stroke=0)
    
    # Formes décoratives aux angles (Rose #E91E63)
    c.setFillColorRGB(0.91, 0.12, 0.39) 
    
    # Angle Haut-Droit
    p1 = c.beginPath()
    p1.moveTo(width, height)
    p1.lineTo(width - 20*mm, height)
    p1.lineTo(width, height - 20*mm)
    p1.close()
    c.drawPath(p1, fill=1, stroke=0)
    
    # Angle Bas-Gauche
    p2 = c.beginPath()
    p2.moveTo(0, 0)
    p2.lineTo(0, 20*mm)
    p2.lineTo(20*mm, 0)
    p2.close()
    c.drawPath(p2, fill=1, stroke=0)

    # --- LOGO & EN-TÊTE ---
    # Logo: Haut Gauche
    logo_file = 'comsas.png'
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', logo_file)
    header_y = height - 12*mm
    
    if os.path.exists(logo_path):
        try:
            c.drawImage(logo_path, 3*mm, height - 13*mm, width=10*mm, height=10*mm, mask='auto', preserveAspectRatio=True)
        except:
            pass
            
    # Titre Principal
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(15*mm, height - 8*mm, "Computer Science Association")
    
    # Sous-titre
    c.setFont("Helvetica", 6)
    c.setFillColorRGB(0.3, 0.3, 0.3)
    c.drawString(15*mm, height - 11*mm, "Club Informatique de l'Université de Yaoundé 1")
    
    # Ligne de séparation fine
    c.setStrokeColorRGB(0.91, 0.12, 0.39)
    c.setLineWidth(0.5)
    c.line(3*mm, height - 15*mm, width - 3*mm, height - 15*mm)
    
    # --- PHOTO (Gauche) ---
    photo_x = 4*mm
    photo_y = 14*mm 
    photo_w = 20*mm
    photo_h = 24*mm
    
    # Cadre photo
    c.setStrokeColorRGB(0.8, 0.8, 0.8)
    c.rect(photo_x, photo_y, photo_w, photo_h, fill=0, stroke=1)
    
    if member.photo:
        try:
            c.drawImage(member.photo.path, photo_x, photo_y, width=photo_w, height=photo_h, mask='auto', preserveAspectRatio=True, anchor='c')
        except:
            c.setFont("Helvetica", 5)
            c.drawCentredString(photo_x + photo_w/2, photo_y + photo_h/2, "Photo")
    else:
        c.setFont("Helvetica", 5)
        c.drawCentredString(photo_x + photo_w/2, photo_y + photo_h/2, "No Photo")
            
    # --- INFORMATIONS (Centre/Droite) ---
    text_x = 28*mm
    
    # Titre de la carte
    c.setFont("Helvetica-Bold", 9)
    c.setFillColorRGB(0.91, 0.12, 0.39) # Pink
    c.drawString(text_x, 34*mm, "CARTE DE MEMBRE")
    
    # Texte de certification
    c.setFont("Helvetica", 7)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(text_x, 30*mm, "Nous certifions que :")
    
    # Nom du membre
    c.setFont("Helvetica-Bold", 11)
    c.drawString(text_x, 26*mm, f"{member.nom_prenom.upper()}")
    
    # Statut / Poste
    status_line = "Membre Actif"
    if member.member_type == 'bureau' and getattr(member, 'poste_bureau', None):
         status_line = member.poste_bureau
    elif member.member_type == 'founder':
         status_line = "Membre Fondateur"
         
    c.setFont("Helvetica", 8)
    c.setFillColorRGB(0.2, 0.2, 0.2)
    c.drawString(text_x, 22*mm, status_line)
    
    # Détails Ligne 1: Matricule et Niveau
    c.setFont("Helvetica", 7)
    c.drawString(text_x, 18.5*mm, f"Matricule: {member.matricule or 'N/A'}")
    
    niveau_text = getattr(member, 'get_niveau_display', lambda: getattr(member, 'niveau', 'N/A'))() or getattr(member, 'promotion', 'N/A')
    c.drawString(text_x + 28*mm, 18.5*mm, f"Niveau: {niveau_text}")

    # Détails Ligne 2: Téléphone
    c.drawString(text_x, 15.5*mm, f"Tél: {member.telephone or 'N/A'}")

    # --- PIED DE PAGE & SIGNATURE ---
    
    # QR Code (Bas Droite)
    qr_size = 12*mm
    qr_x = width - qr_size - 3*mm
    qr_y = 3*mm 
    
    try:
        profile_url = settings.SITE_URL + reverse('member_profile', args=[member.id])
    except:
        profile_url = getattr(settings, 'SITE_URL', 'https://comsas-uy1.com') + f"/membre/{member.id}"
        
    qr = qrcode.QRCode(box_size=2, border=0)
    qr.add_data(profile_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer)
    qr_buffer.seek(0)
    
    c.drawImage(ImageReader(qr_buffer), qr_x, qr_y, width=qr_size, height=qr_size)
    
    # Signature (Image) - Bas Centre
    # Positionnement plus serré
    label_x = text_x + 15*mm # Décalé un peu vers la droite pour centrer dans l'espace vide
    label_y = 12*mm 
    
    c.setFont("Helvetica-Oblique", 6)
    c.setFillColorRGB(0, 0, 0)
    c.drawCentredString(label_x, label_y, "Le Président du COMS.A.S")
    
    sig_file = os.path.join(settings.BASE_DIR, 'static', 'images', 'signature.png')
    
    if os.path.exists(sig_file):
        try:
            # Signature
            c.drawImage(sig_file, label_x - 15*mm, 3*mm, width=30*mm, height=8.5*mm, mask='auto', preserveAspectRatio=True)
            
            # Nom
            c.setFont("Helvetica-Bold", 6)
            c.drawCentredString(label_x, 2*mm, "Neussi Patrice .E ")
        except Exception as e:
            c.setFont("Helvetica", 5)
            c.drawCentredString(label_x, 5*mm, "Neussi Patrice .E")
    else:
        c.setFont("Helvetica-Bold", 6)
        c.drawCentredString(label_x, 5*mm, "Neussi Patrice .E")
    
    c.showPage()
    c.save()
    
    buffer.seek(0)
    return buffer

def send_member_card_email(member, pdf_buffer):
    """
    Envoie l'email de validation avec la carte de membre.
    """
    try:
        # Envoyer Email
        email_subject = "Votre adhésion au COMS.A.S est validée !"
        
        try:
             profile_url = f"{settings.SITE_URL}{reverse('member_profile', args=[member.id])}"
        except:
             profile_url = getattr(settings, 'SITE_URL', 'https://comsas-uy1.com') + f"/membre/{member.id}/"
             
        # Context for template
        context = {
            'member': member,
            'profile_url': profile_url,
            'site_url': getattr(settings, 'SITE_URL', 'https://comsas-uy1.com'),
        }
        
        # Render HTML
        from django.template.loader import render_to_string
        from django.utils.html import strip_tags
        from django.core.mail import EmailMultiAlternatives
        
        html_content = render_to_string('emails/member_card.html', context)
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            email_subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [member.email],
        )
        email.attach_alternative(html_content, "text/html")
        email.attach(f'carte_membre_{member.matricule or member.id}.pdf', pdf_buffer.getvalue(), 'application/pdf')
        
        email.send(fail_silently=False)
        return True
            
    except Exception as e:
        print(f"Erreur envoi email validation pour {member.nom_prenom}: {e}")
        return False


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
