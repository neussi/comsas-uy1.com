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
    Génère une carte de membre officielle au format PDF.
    Taille standard CR80 (85.6mm x 54mm) - Charte officielle Rose et Blanc du COMSAS.
    """
    from reportlab.lib.units import mm
    
    width, height = 85.6 * mm, 54 * mm
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=(width, height))
    
    # 1. Fond blanc pur (AUCUN QUADRILLAGE)
    c.setFillColor(colors.white)
    c.rect(0, 0, width, height, fill=1, stroke=0)
    
    # 2. Couleurs officielles Rose et Blanc
    ROSE_COMSAS = colors.HexColor('#E91E63')
    ROSE_DARK = colors.HexColor('#C2185B')
    ROSE_LIGHT = colors.HexColor('#FCE4EC')
    TEXT_DARK = colors.HexColor('#1A0A10')
    TEXT_MUTED = colors.HexColor('#6B7280')

    # Bandeau supérieur Rose COMSAS
    c.setFillColor(ROSE_COMSAS)
    c.rect(0, height - 3.5*mm, width, 3.5*mm, fill=1, stroke=0)
    
    # Liseré rose inférieur
    c.setFillColor(ROSE_DARK)
    c.rect(0, 0, width, 1.5*mm, fill=1, stroke=0)

    # 3. Logo et En-tête
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'comsas.png')
    if os.path.exists(logo_path):
        try:
            c.drawImage(logo_path, 3.5*mm, height - 13*mm, width=8.5*mm, height=8.5*mm, mask='auto', preserveAspectRatio=True)
        except Exception:
            pass

    c.setFillColor(ROSE_DARK)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(13.5*mm, height - 8.5*mm, "COMPUTER SCIENCE ASSOCIATION")
    
    c.setFont("Helvetica", 5.5)
    c.setFillColor(TEXT_MUTED)
    c.drawString(13.5*mm, height - 11.5*mm, "Club Informatique de l'Université de Yaoundé 1")

    # Ligne de séparation fine rose
    c.setStrokeColor(ROSE_COMSAS)
    c.setLineWidth(0.6)
    c.line(3.5*mm, height - 14*mm, width - 3.5*mm, height - 14*mm)

    # 4. Photo du membre (Gauche)
    photo_x = 4*mm
    photo_y = 6*mm
    photo_w = 21*mm
    photo_h = 28*mm
    
    c.setFillColor(ROSE_LIGHT)
    c.rect(photo_x, photo_y, photo_w, photo_h, fill=1, stroke=0)
    c.setStrokeColor(ROSE_COMSAS)
    c.setLineWidth(0.8)
    c.rect(photo_x, photo_y, photo_w, photo_h, fill=0, stroke=1)

    if member.photo and hasattr(member.photo, 'path') and os.path.exists(member.photo.path):
        try:
            c.drawImage(member.photo.path, photo_x, photo_y, width=photo_w, height=photo_h, mask='auto', preserveAspectRatio=True, anchor='c')
        except Exception:
            c.setFont("Helvetica", 6)
            c.setFillColor(TEXT_MUTED)
            c.drawCentredString(photo_x + photo_w/2, photo_y + photo_h/2, "Photo")
    else:
        c.setFont("Helvetica-Bold", 6)
        c.setFillColor(ROSE_COMSAS)
        c.drawCentredString(photo_x + photo_w/2, photo_y + photo_h/2, "COMSAS")

    # 5. Informations personnelles (Centre)
    tx = 28*mm
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(ROSE_COMSAS)
    c.drawString(tx, height - 18.5*mm, "CARTE DE MEMBRE")

    # Nom et prénom du membre avec mise à l'échelle automatique
    nom_affiche = (member.nom_prenom or '').upper()
    qr_size = 11*mm
    qr_x = width - qr_size - 4*mm
    max_text_width = qr_x - tx - 2*mm
    nom_font_size = 9.0
    while nom_font_size > 6.0 and stringWidth(nom_affiche, "Helvetica-Bold", nom_font_size) > max_text_width:
        nom_font_size -= 0.5
    c.setFont("Helvetica-Bold", nom_font_size)
    c.setFillColor(TEXT_DARK)
    c.drawString(tx, height - 23*mm, nom_affiche)

    # Statut / Rôle
    status = "Membre Actif"
    if member.member_type == 'bureau' and getattr(member, 'poste_bureau', None):
        status = member.poste_bureau
    elif member.member_type == 'founder':
        status = "Membre Fondateur"

    role_font_size = 7.5
    while role_font_size > 5.5 and stringWidth(status, "Helvetica-Bold", role_font_size) > max_text_width:
        role_font_size -= 0.5
    c.setFont("Helvetica-Bold", role_font_size)
    c.setFillColor(ROSE_DARK)
    c.drawString(tx, height - 26.5*mm, status)

    # Coordonnées et Niveau académique
    c.setFont("Helvetica", 6.5)
    c.setFillColor(TEXT_DARK)
    c.drawString(tx, height - 30.5*mm, f"Matricule : {member.matricule or 'Non renseigné'}")
    
    niveau_nom = getattr(member, 'get_niveau_display', lambda: getattr(member, 'niveau', 'N/A'))() or getattr(member, 'promotion', 'N/A')
    c.drawString(tx, height - 34*mm, f"Niveau : {niveau_nom}")
    c.drawString(tx, height - 37.5*mm, f"Téléphone : {member.telephone or 'N/A'}")

    # 6. QR Code de vérification (Droite)
    profile_url = f"{getattr(settings, 'SITE_URL', 'https://comsas-uy1.com')}/membre/{member.id}"
    qr_size = 11*mm
    qr_x = width - qr_size - 4*mm
    qr_y = height - 26*mm

    qr = qrcode.QRCode(box_size=1, border=0)
    qr.add_data(profile_url)
    qr.make(fit=True)
    qimg = qr.make_image(fill_color="#C2185B", back_color="white")
    qb = BytesIO()
    qimg.save(qb)
    qb.seek(0)
    c.drawImage(ImageReader(qb), qr_x, qr_y, width=qr_size, height=qr_size)

    # 7. Signature et Cachet officiel du Président (En bas à droite)
    sig_center_x = width - 17*mm
    c.setFont("Helvetica-Bold", 6.2)
    c.setFillColor(TEXT_DARK)
    c.drawCentredString(sig_center_x, 11*mm, "Le Président du COMS.A.S")

    sig_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'signature.png')
    if os.path.exists(sig_path):
        try:
            c.drawImage(sig_path, sig_center_x - 11*mm, 2*mm, width=22*mm, height=9*mm, mask='auto', preserveAspectRatio=True)
        except Exception:
            pass

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
