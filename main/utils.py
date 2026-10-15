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


def render_ticket_pdf(event, participant_data):
    """
    Rendu graphique du Billet VIP officiel (Format Boarding Pass de prestige).
    Comprend une souche détachable avec encoches d'arrachage, logos UY1 et COMSAS,
    titre percutant, informations précises, consignes d'accès et QR code de sécurité.
    """
    from reportlab.lib.units import inch, mm
    
    buffer = BytesIO()
    ticket_width, ticket_height = 8.5 * inch, 3.4 * inch  # ~216mm x 86.4mm
    p = canvas.Canvas(buffer, pagesize=(ticket_width, ticket_height))

    # Palette
    C_NAVY_DARK = colors.HexColor('#0A1128')
    C_BLUE_ROYAL = colors.HexColor('#0052D4')
    C_BLUE_CYAN = colors.HexColor('#00D2FF')
    C_GOLD_MAIN = colors.HexColor('#D4AF37')
    C_GOLD_LIGHT = colors.HexColor('#F9D776')
    C_TEXT_NAVY = colors.HexColor('#0F172A')
    C_TEXT_MUTED = colors.HexColor('#64748B')
    C_BG_OFFWHITE = colors.HexColor('#F8FAFC')

    # 1. Fond général du billet
    p.setFillColor(colors.white)
    p.rect(0, 0, ticket_width, ticket_height, fill=1, stroke=0)

    # 2. Souche détachable à gauche (Stub)
    stub_width = 2.1 * inch
    p.setFillColor(C_NAVY_DARK)
    p.rect(0, 0, stub_width, ticket_height, fill=1, stroke=0)

    # Accent doré sur la tranche gauche
    p.setFillColor(C_GOLD_MAIN)
    p.rect(0, 0, 3 * mm, ticket_height, fill=1, stroke=0)

    # Motifs géométriques subtils sur la souche
    p.setStrokeColor(colors.HexColor('#1E293B'))
    p.setLineWidth(0.5)
    for i in range(8):
        p.line(8 * mm, 10 * mm + i * 8 * mm, stub_width - 8 * mm, 10 * mm + i * 8 * mm)

    # Code-barres décoratif vertical sur la souche (Partie basse)
    p.saveState()
    barcode_x = 9 * mm
    barcode_y = 11 * mm
    barcode_h = 13 * mm
    p.setFillColor(colors.white)
    bar_widths = [1.2, 0.6, 2.0, 0.8, 1.5, 0.5, 1.8, 0.7, 2.2, 0.6, 1.0, 1.6, 0.5, 1.4, 0.9, 2.1, 0.6, 1.1]
    cur_bx = barcode_x
    for bw in bar_widths:
        p.rect(cur_bx, barcode_y, bw, barcode_h, fill=1, stroke=0)
        cur_bx += bw + 1.2 * mm
    p.restoreState()

    # ID court sous le code-barres
    p.setFont("Helvetica", 6.5)
    p.setFillColor(colors.HexColor('#94A3B8'))
    uuid_str = str(participant_data.get('uuid', 'TICKET-2026'))
    p.drawCentredString(stub_width / 2 + 1 * mm, 5 * mm, f"N° {uuid_str[:15]}")

    # Texte pivoté à 90° sur la souche (Partie haute)
    p.saveState()
    p.translate(stub_width / 2 + 2.5 * mm, ticket_height * 0.62)
    p.rotate(90)
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 10.5)
    p.drawCentredString(0, 0, "BILLET D'ACCÈS • PASS VIP")
    p.setFont("Helvetica-Bold", 8.5)
    p.setFillColor(C_GOLD_LIGHT)
    date_formatted = event.date_event.strftime('%d.%m.%Y • %H:%M') if getattr(event, 'date_event', None) else "DATE À DÉFINIR"
    p.drawCentredString(0, -4.2 * mm, date_formatted)
    p.restoreState()

    # Ligne de perforation (tirets) et encoches de découpe
    p.setStrokeColor(colors.HexColor('#CBD5E1'))
    p.setLineWidth(1)
    p.setDash(3, 3)
    p.line(stub_width, 0, stub_width, ticket_height)
    p.setDash()  # reset dash

    # Encoches semi-circulaires d'arrachage au haut et au bas de la ligne de découpe
    p.setFillColor(colors.white)
    p.circle(stub_width, ticket_height, 4 * mm, fill=1, stroke=0)
    p.circle(stub_width, 0, 4 * mm, fill=1, stroke=0)
    p.setStrokeColor(colors.HexColor('#E2E8F0'))
    p.setLineWidth(0.6)
    p.circle(stub_width, ticket_height, 4 * mm, fill=0, stroke=1)
    p.circle(stub_width, 0, 4 * mm, fill=0, stroke=1)

    # 3. Corps Principal du Billet (Main Content)
    main_x = stub_width + 8 * mm
    main_top = ticket_height - 8 * mm

    # Logos : UY1 EN PREMIER et Agrandit, puis COMSAS
    uy1_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'uy1.png')
    comsas_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'comsas.png')
    
    logo_size = 13 * mm
    if os.path.exists(uy1_path):
        try:
            p.drawImage(ImageReader(uy1_path), main_x, main_top - logo_size + 1 * mm, width=logo_size, height=logo_size, mask='auto', preserveAspectRatio=True)
        except Exception:
            pass

    if os.path.exists(comsas_path):
        try:
            p.drawImage(ImageReader(comsas_path), main_x + logo_size + 3 * mm, main_top - logo_size + 1 * mm, width=logo_size, height=logo_size, mask='auto', preserveAspectRatio=True)
        except Exception:
            pass

    # Titre institutionnel
    inst_x = main_x + logo_size * 2 + 6 * mm
    p.setFont("Helvetica-Bold", 8)
    p.setFillColor(C_TEXT_NAVY)
    p.drawString(inst_x, main_top - 3 * mm, "UNIVERSITÉ DE YAOUNDÉ 1 • FACULTÉ DES SCIENCES")
    p.setFont("Helvetica", 6.8)
    p.setFillColor(C_TEXT_MUTED)
    p.drawString(inst_x, main_top - 7 * mm, "Département d'Informatique • Computer Science Association (COMSAS)")

    # Badge Pilule "OFFICIEL" en haut à droite
    pill_w = 32 * mm
    pill_h = 5.5 * mm
    pill_rx = ticket_width - pill_w - 7 * mm
    pill_ry = main_top - 6 * mm
    p.setFillColor(C_BLUE_ROYAL)
    p.roundRect(pill_rx, pill_ry, pill_w, pill_h, 2 * mm, fill=1, stroke=0)
    p.setFont("Helvetica-Bold", 6.5)
    p.setFillColor(colors.white)
    p.drawCentredString(pill_rx + pill_w / 2, pill_ry + 1.6 * mm, "BILLET OFFICIEL D'ACCÈS")

    # Filet fin de séparation sous l'en-tête
    sep_y = main_top - logo_size - 2 * mm
    p.setStrokeColor(colors.HexColor('#E2E8F0'))
    p.setLineWidth(0.8)
    p.line(main_x, sep_y, ticket_width - 7 * mm, sep_y)

    # 4. Titre de l'événement (En grand)
    event_title = getattr(event, 'title_fr', "Événement Officiel").upper()
    p.setFont("Helvetica-Bold", 12.5)
    p.setFillColor(C_BLUE_ROYAL)
    
    # Adaptation du titre si long
    max_title_w = ticket_width - main_x - 38 * mm
    if stringWidth(event_title, "Helvetica-Bold", 12.5) > max_title_w:
        p.setFont("Helvetica-Bold", 10.5)
    
    p.drawString(main_x, sep_y - 6 * mm, event_title)

    # 5. Détails du Participant & Événement (Grille élégante)
    details_y = sep_y - 12 * mm

    # Nom du Participant
    p.setFont("Helvetica-Bold", 7.5)
    p.setFillColor(C_GOLD_MAIN)
    p.drawString(main_x, details_y, "PARTICIPANT")
    
    p.setFont("Helvetica-Bold", 11)
    p.setFillColor(C_TEXT_NAVY)
    nom_part = participant_data.get('nom_prenom', 'Patrice Nguekam Dassi').upper()
    p.drawString(main_x, details_y - 4.5 * mm, nom_part)

    # Date et Lieu
    p.setFont("Helvetica-Bold", 7)
    p.setFillColor(C_TEXT_MUTED)
    p.drawString(main_x, details_y - 10.5 * mm, "DATE & HEURE :")
    p.setFont("Helvetica-Bold", 8)
    p.setFillColor(C_TEXT_NAVY)
    date_val = event.date_event.strftime('%d %B %Y à %H:%M') if getattr(event, 'date_event', None) else "À confirmer"
    p.drawString(main_x + 24 * mm, details_y - 10.5 * mm, date_val)

    p.setFont("Helvetica-Bold", 7)
    p.setFillColor(C_TEXT_MUTED)
    p.drawString(main_x, details_y - 15.5 * mm, "LIEU / SALLE :")
    p.setFont("Helvetica-Bold", 8)
    p.setFillColor(C_TEXT_NAVY)
    loc_val = getattr(event, 'location', 'Campus UY1') or "Campus Universitaire de Yaoundé 1"
    p.drawString(main_x + 24 * mm, details_y - 15.5 * mm, loc_val[:48])

    # Consigne personnalisable (ticket_note)
    ticket_note = getattr(event, 'ticket_note', '') or "Billet officiel d'accès - Présentez ce ticket et votre pièce d'identité à l'entrée."
    p.setFont("Helvetica-Oblique", 6.2)
    p.setFillColor(C_TEXT_MUTED)
    p.drawString(main_x, 6 * mm, ticket_note[:90])

    # 6. QR Code de Sécurité & Validation à droite
    qr_s = 25 * mm
    qx = ticket_width - qr_s - 7 * mm
    qy = 12 * mm

    verify_url = participant_data.get('verify_url') or f"{getattr(settings, 'SITE_URL', 'https://comsas-uy1.com')}/verify/{uuid_str}"

    qr = qrcode.QRCode(box_size=6, border=0)
    qr.add_data(verify_url)
    qr.make(fit=True)
    qr_buf = BytesIO()
    qr.make_image(fill_color="#0A1128", back_color="white").save(qr_buf, 'PNG')
    qr_buf.seek(0)

    # Cadre fin autour du QR
    p.setStrokeColor(colors.HexColor('#E2E8F0'))
    p.setLineWidth(0.6)
    p.rect(qx - 1.5 * mm, qy - 1.5 * mm, qr_s + 3 * mm, qr_s + 3 * mm, fill=0, stroke=1)
    
    p.drawImage(ImageReader(qr_buf), qx, qy, width=qr_s, height=qr_s)

    p.setFont("Helvetica-Bold", 5.5)
    p.setFillColor(C_BLUE_ROYAL)
    p.drawCentredString(qx + qr_s / 2, qy - 4.5 * mm, "SCAN POUR ACCÈS EN SALLE")

    # Bordure générale extérieure fine
    p.setStrokeColor(colors.HexColor('#CBD5E1'))
    p.setLineWidth(0.8)
    p.rect(1 * mm, 1 * mm, ticket_width - 2 * mm, ticket_height - 2 * mm, fill=0, stroke=1)

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer


def generate_ticket(registration):
    """
    Génère et sauvegarde le billet officiel pour une inscription.
    """
    event = registration.event
    verify_url = f"{getattr(settings, 'SITE_URL', 'https://comsas-uy1.com')}{reverse('ticket_verify', kwargs={'uuid': registration.uuid})}"

    # Sauvegarde du QR code image pour le modèle
    qr = qrcode.QRCode(version=1, box_size=8, border=2)
    qr.add_data(verify_url)
    qr.make(fit=True)
    blob = BytesIO()
    qr.make_image(fill_color="black", back_color="white").save(blob, 'PNG')
    registration.qr_code.save(f'qr_{registration.uuid}.png', File(blob), save=False)

    participant_data = {
        'nom_prenom': registration.nom_prenom,
        'promotion': getattr(registration, 'promotion', ''),
        'uuid': registration.uuid,
        'verify_url': verify_url,
    }

    buffer = render_ticket_pdf(event, participant_data)
    
    if registration.ticket_pdf:
        registration.ticket_pdf.delete(save=False)

    registration.ticket_pdf.save(f'ticket_{registration.uuid}.pdf', File(buffer), save=True)
    return registration.ticket_pdf.url


def generate_preview_ticket(event):
    """
    Génère un billet PDF de démonstration pour la prévisualisation dans l'admin.
    """
    participant_data = {
        'nom_prenom': 'Patrice Nguekam Dassi',
        'promotion': 'Master 1 Génie Logiciel',
        'uuid': 'PREVIEW-TICKET-2026',
        'verify_url': f"{getattr(settings, 'SITE_URL', 'https://comsas-uy1.com')}/verify/preview",
    }
    return render_ticket_pdf(event, participant_data)
