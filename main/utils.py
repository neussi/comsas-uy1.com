import qrcode
from io import BytesIO
from django.core.files import File
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
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
    # --- FOND & DESIGN (Premium Tech Theme) ---
    ORANGE_MANDAT = colors.Color(243/255, 146/255, 0/255)
    TECH_DARK = colors.Color(31/255, 41/255, 55/255)
    
    # Background
    c.setFillColor(TECH_DARK)
    c.rect(0, 0, width, height, fill=1, stroke=0)
    
    # Tech Grid Layer
    c.setStrokeColor(colors.white)
    c.setLineWidth(0.05)
    for i in range(0, int(width), int(5*mm)): c.line(i, 0, i, height)
    for i in range(0, int(height), int(5*mm)): c.line(0, i, width, i)

    # Accent Top Bar
    c.setFillColor(ORANGE_MANDAT)
    c.rect(0, height - 3*mm, width, 3*mm, fill=1, stroke=0)
    
    # --- LOGO & Identity ---
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'comsas.png')
    if os.path.exists(logo_path):
        try: c.drawImage(logo_path, 2*mm, height - 12*mm, width=8*mm, height=8*mm, mask='auto', preserveAspectRatio=True)
        except: pass
            
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 7)
    c.drawString(11*mm, height - 8*mm, "COMPUTER SCIENCE ASSOCIATION")
    c.setFont("Helvetica", 4.5)
    c.drawString(11*mm, height - 10.5*mm, "Club Informatique de l'Université de Yaoundé 1")
    
    # --- Body Content (Card within Card for Contrast) ---
    inner_x, inner_y = 2*mm, 2*mm 
    inner_w, inner_h = width - 4*mm, height - 15*mm 
    c.setFillColor(colors.white)
    c.rect(inner_x, inner_y, inner_w, inner_h, fill=1, stroke=0)
    
    # --- Member Photo ---
    photo_x, photo_y = 4*mm, 10*mm 
    photo_w, photo_h = 24*mm, 28*mm
    c.setStrokeColor(ORANGE_MANDAT)
    c.setLineWidth(1)
    c.rect(photo_x, photo_y, photo_w, photo_h, fill=0, stroke=1)
    
    if member.photo:
        try: c.drawImage(member.photo.path, photo_x, photo_y, width=photo_w, height=photo_h, mask='auto', preserveAspectRatio=True, anchor='c')
        except: pass
            
    # --- Details ---
    tx = 30*mm
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(ORANGE_MANDAT)
    c.drawString(tx, 32*mm, "CARTE DE MEMBRE")
    
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(TECH_DARK)
    c.drawString(tx, 27*mm, f"{member.nom_prenom.upper()}")
    
    status = "Membre Actif"
    if member.member_type == 'bureau' and getattr(member, 'poste_bureau', None): status = member.poste_bureau
    
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(ORANGE_MANDAT)
    c.drawString(tx, 23*mm, status)
    
    c.setFont("Helvetica", 6)
    c.setFillColor(colors.gray)
    c.drawString(tx, 19*mm, f"ID: {member.matricule or 'N/A'}")
    c.drawString(tx, 16*mm, f"Niveau: {getattr(member, 'niveau', 'N/A')}")
    c.drawString(tx, 13*mm, f"Tél: {member.telephone or 'N/A'}")

    # --- Officiality Section ---
    sig_y_label = 11*mm
    lx = width - 20*mm
    c.setFont("Helvetica-Bold", 6)
    c.setFillColor(TECH_DARK)
    c.drawCentredString(lx, sig_y_label, "Le Président du COMS.A.S")
    
    # Signature/Stamp BELOW THE LABEL
    sig_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'signature.png')
    if os.path.exists(sig_path):
        c.drawImage(sig_path, lx - 12*mm, 2*mm, width=24*mm, height=12*mm, mask='auto', preserveAspectRatio=True)

    # QR Code Verification
    qx, qy, qs = width - 11*mm, 15*mm, 7*mm
    qr = qrcode.QRCode(box_size=1, border=0)
    qr.add_data(profile_url)
    qr.make(fit=True)
    qimg = qr.make_image(fill_color="black", back_color="white")
    qb = BytesIO()
    qimg.save(qb)
    qb.seek(0)
    c.drawImage(ImageReader(qb), qx, qy, width=qs, height=qs)
    
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
    ticket_width, ticket_height = 8.5 * inch, 3.5 * inch
    p = canvas.Canvas(buffer, pagesize=(ticket_width, ticket_height))
    
    # Orange Mandat Theme
    ORANGE_MANDAT = colors.Color(243/255, 146/255, 0/255) # #F39200
    TECH_GRAY = colors.Color(45/255, 45/255, 45/255)
    
    p.setFillColor(colors.white)
    p.rect(0, 0, ticket_width, ticket_height, fill=1, stroke=0)
    
    # Stub background (Orange)
    stub_width = 1.8*inch
    p.setFillColor(ORANGE_MANDAT)
    p.rect(0, 0, stub_width, ticket_height, fill=1, stroke=0)
    
    # Tech accents on stub
    p.setStrokeColor(colors.white)
    p.setLineWidth(0.5)
    for i in range(12):
        p.line(0.2*inch, 0.4*inch + i*0.2*inch, stub_width - 0.2*inch, 0.4*inch + i*0.2*inch)

    p.saveState()
    p.translate(stub_width/2 + 0.1*inch, ticket_height/2)
    p.rotate(90)
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(0, 0, "ADMIT ONE")
    p.setFont("Helvetica", 10)
    p.drawCentredString(0, -0.3*inch, registration.event.date_event.strftime('%d.%m.%Y'))
    p.restoreState()
    
    # --- Main Content ---
    content_x = stub_width + 0.4*inch
    
    # Logos
    logo_size, ly = 0.7*inch, ticket_height - 1.1*inch
    logos = []
    comsas_path = os.path.join(settings.BASE_DIR, 'static/images/comsas.png')
    if os.path.exists(comsas_path): logos.append(comsas_path)
    if registration.event.partner_logo_1: logos.append(registration.event.partner_logo_1.path)
    if registration.event.partner_logo_2: logos.append(registration.event.partner_logo_2.path)
    
    for i, lp in enumerate(logos[:3]):
        try: p.drawImage(ImageReader(lp), content_x + i*0.8*inch, ly, width=logo_size, height=logo_size, mask='auto', preserveAspectRatio=True)
        except: pass
        
    p.setFillColor(TECH_GRAY)
    p.setFont("Helvetica-Bold", 34)
    p.drawRightString(ticket_width - 0.5*inch, ticket_height - 0.95*inch, "TICKET")
    
    # Title
    y_title = ly - 0.6*inch
    p.setFillColor(ORANGE_MANDAT)
    p.setFont("Helvetica-Bold", 16)
    title = registration.event.title_fr.upper()
    max_w = ticket_width - content_x - 1.8*inch
    
    if stringWidth(title, "Helvetica-Bold", 16) > max_w:
        p.setFont("Helvetica-Bold", 12)
        if stringWidth(title, "Helvetica-Bold", 12) > max_w:
            words = title.split()
            l1, l2 = "", ""
            for w in words:
                if stringWidth(l1 + " " + w, "Helvetica-Bold", 12) < max_w: l1 += " " + w if l1 else w
                else: l2 += " " + w if l2 else w
            p.drawString(content_x, y_title, l1)
            p.drawString(content_x, y_title - 0.2*inch, l2)
            y_title -= 0.3*inch
        else: p.drawString(content_x, y_title, title)
    else: p.drawString(content_x, y_title, title)
    
    # QR Code
    qr_s = 1.1*inch
    qx, qy = ticket_width - qr_s - 0.4*inch, 0.6*inch
    if 'blob' in locals():
        blob.seek(0)
        p.drawImage(ImageReader(blob), qx, qy, width=qr_s, height=qr_s)
    
    p.setFont("Helvetica", 7)
    p.setFillColor(colors.gray)
    p.drawCentredString(qx + qr_s/2, qy - 0.15*inch, "SCAN & VERIFY")
    
    # Info
    y_info = y_title - 0.6*inch
    p.setFont("Helvetica", 10)
    p.setFillColor(TECH_GRAY)
    p.drawString(content_x, y_info, f"DATE: {registration.event.date_event.strftime('%d %B %Y • %H:%M')}")
    p.drawString(content_x, y_info - 0.2*inch, f"LIEU: {registration.event.location[:50]}")
    
    y_part = y_info - 0.5*inch
    p.setFont("Helvetica-Bold", 11)
    p.setFillColor(ORANGE_MANDAT)
    p.drawString(content_x, y_part, "PARTICIPANT:")
    p.setFillColor(TECH_GRAY)
    p.drawString(content_x + 1.1*inch, y_part, registration.nom_prenom.upper())
    
    # Footer
    p.setFont("Helvetica", 7)
    p.setFillColor(colors.gray)
    p.drawString(0.2*inch, 0.15*inch, f"ID: {str(registration.uuid)[:13]}")
    p.drawRightString(ticket_width - 0.2*inch, 0.15*inch, "COMS.A.S • Université de Yaoundé 1")
    
    p.showPage()
    p.save()
    buffer.seek(0)
    registration.ticket_pdf.save(f'ticket_{registration.uuid}.pdf', File(buffer), save=True)
    return registration.ticket_pdf.url
