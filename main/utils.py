import os
import qrcode
from io import BytesIO
from django.conf import settings
from django.urls import reverse
from django.core.mail import EmailMessage
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from PIL import Image

def generate_member_card(member):
    """
    Génère une carte de membre professionnelle au format PDF.
    Taille standard CR80 (85.6mm x 53.98mm).
    """
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
    if member.member_type == 'bureau' and member.poste_bureau:
         status_line = member.poste_bureau
    elif member.member_type == 'founder':
         status_line = "Membre Fondateur"
         
    c.setFont("Helvetica", 8)
    c.setFillColorRGB(0.2, 0.2, 0.2)
    c.drawString(text_x, 22*mm, status_line)
    
    # Détails Ligne 1: Matricule et Niveau
    c.setFont("Helvetica", 7)
    c.drawString(text_x, 18.5*mm, f"Matricule: {member.matricule or 'N/A'}")
    c.drawString(text_x + 28*mm, 18.5*mm, f"Niveau: {member.niveau or 'N/A'}")

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
        profile_url = f"https://comsas-uy1.com/membre/{member.id}"
        
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
            c.drawCentredString(label_x, 2*mm, "Mfenjou anas Cherif ")
        except Exception as e:
            c.setFont("Helvetica", 5)
            c.drawCentredString(label_x, 5*mm, "Mfenjou anas Cherif")
    else:
        c.setFont("Helvetica", 5)
        c.drawCentredString(label_x, 5*mm, "Mfenjou anas Cherif")
    
    c.showPage()
    c.save()
    
    buffer.seek(0)
    return buffer

def send_member_card_email(member):
    """
    Envoie l'email de validation (sans la carte PDF).
    Retourne True si succès, False sinon.
    """
    try:
        # Envoyer Email
        email_subject = "Votre adhésion au COMS.A.S est validée !"
        
        try:
             profile_url = f"{settings.SITE_URL}{reverse('member_profile', args=[member.id])}"
        except:
             profile_url = f"https://comsas-uy1.com/membre/{member.id}/"
             
        # Context for template
        context = {
            'member': member,
            'profile_url': profile_url,
            'site_url': settings.SITE_URL,
        }
        
        # Render HTML
        from django.template.loader import render_to_string
        from django.utils.html import strip_tags
        from django.core.mail import EmailMultiAlternatives
        
        html_content = render_to_string('emails/member_card.html', context)
        text_content = strip_tags(html_content) # Fallback simple

        email = EmailMultiAlternatives(
            email_subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [member.email],
        )
        email.attach_alternative(html_content, "text/html")
        # PDF Attachment removed as per request
        
        email.send(fail_silently=False)
        return True
            
    except Exception as e:
        print(f"Erreur envoi email validation pour {member.nom_prenom}: {e}")
        return False
