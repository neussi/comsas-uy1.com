import qrcode
import os
from io import BytesIO
from django.core.files import File
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth
from django.utils import timezone
from django.conf import settings
from django.urls import reverse


def generate_certificate(registration):
    """
    Génère une attestation / certificat officiel de participation.
    Format A4 Paysage - Charte officielle Rose et Blanc du COMSAS (sans quadrillage ni carrés).
    """
    event = registration.event
    
    if not getattr(event, 'certificate_enabled', True):
        return None

    buffer = BytesIO()
    # Format A4 Paysage
    page_height, page_width = A4
    p = canvas.Canvas(buffer, pagesize=(page_width, page_height))
    
    # Couleurs officielles COMSAS
    ROSE_COMSAS = colors.HexColor('#E91E63')
    ROSE_DARK = colors.HexColor('#C2185B')
    ROSE_PALE = colors.HexColor('#FCE4EC')
    TEXT_DARK = colors.HexColor('#1A0A10')
    TEXT_MUTED = colors.HexColor('#555555')

    # 1. Fond blanc pur (AUCUN QUADRILLAGE)
    p.setFillColor(colors.white)
    p.rect(0, 0, page_width, page_height, fill=1, stroke=0)

    # 2. Cadre d'honneur diplomatique double-filet Rose COMSAS
    # Filet extérieur
    p.setStrokeColor(ROSE_COMSAS)
    p.setLineWidth(2)
    p.rect(10*mm, 10*mm, page_width - 20*mm, page_height - 20*mm, fill=0, stroke=1)

    # Filet intérieur fin
    p.setStrokeColor(ROSE_DARK)
    p.setLineWidth(0.6)
    p.rect(13*mm, 13*mm, page_width - 26*mm, page_height - 26*mm, fill=0, stroke=1)

    # Coins décoratifs discrets
    c_len = 8*mm
    p.setStrokeColor(ROSE_DARK)
    p.setLineWidth(1.5)
    # Haut gauche
    p.line(10*mm, page_height - 10*mm - c_len, 10*mm, page_height - 10*mm)
    p.line(10*mm, page_height - 10*mm, 10*mm + c_len, page_height - 10*mm)
    # Haut droit
    p.line(page_width - 10*mm - c_len, page_height - 10*mm, page_width - 10*mm, page_height - 10*mm)
    p.line(page_width - 10*mm, page_height - 10*mm, page_width - 10*mm, page_height - 10*mm - c_len)
    # Bas gauche
    p.line(10*mm, 10*mm + c_len, 10*mm, 10*mm)
    p.line(10*mm, 10*mm, 10*mm + c_len, 10*mm)
    # Bas droit
    p.line(page_width - 10*mm - c_len, 10*mm, page_width - 10*mm, 10*mm)
    p.line(page_width - 10*mm, 10*mm, page_width - 10*mm, 10*mm + c_len)

    # 3. Logo officiel COMSAS (Haut gauche)
    comsas_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'comsas.png')
    if os.path.exists(comsas_path):
        try:
            p.drawImage(ImageReader(comsas_path), 20*mm, page_height - 38*mm, width=20*mm, height=20*mm, mask='auto', preserveAspectRatio=True)
        except Exception:
            pass

    # Logo UY1 (Haut droite)
    uy1_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'uy1.png')
    if os.path.exists(uy1_path):
        try:
            p.drawImage(ImageReader(uy1_path), page_width - 40*mm, page_height - 38*mm, width=20*mm, height=20*mm, mask='auto', preserveAspectRatio=True)
        except Exception:
            pass

    # 4. En-tête institutionnel
    p.setFillColor(TEXT_MUTED)
    p.setFont("Helvetica-Bold", 10)
    p.drawCentredString(page_width/2, page_height - 24*mm, "UNIVERSITÉ DE YAOUNDÉ 1 - FACULTÉ DES SCIENCES")
    p.setFont("Helvetica", 8.5)
    p.drawCentredString(page_width/2, page_height - 29*mm, "Département d'Informatique - Computer Science Association (COMSAS)")

    # 5. Titre du Certificat
    p.setFillColor(ROSE_DARK)
    p.setFont("Helvetica-Bold", 36)
    titre_certif = event.certificate_title if getattr(event, 'certificate_title', None) else "ATTESTATION DE PARTICIPATION"
    p.drawCentredString(page_width/2, page_height - 48*mm, titre_certif.upper())

    # Sous-titre décoratif
    p.setFillColor(ROSE_COMSAS)
    p.setFont("Helvetica-Bold", 12)
    p.drawCentredString(page_width/2, page_height - 56*mm, "DÉCERNÉE POUR VALOIR CE QUE DE DROIT")

    # Ligne fine centrale
    p.setStrokeColor(ROSE_COMSAS)
    p.setLineWidth(0.8)
    p.line(page_width*0.35, page_height - 60*mm, page_width*0.65, page_height - 60*mm)

    # 6. Récipiendaire
    p.setFillColor(TEXT_MUTED)
    p.setFont("Helvetica", 13)
    p.drawCentredString(page_width/2, page_height - 72*mm, "La présente attestation est fièrement décernée à :")

    # Nom du participant avec adaptation dynamique de taille
    nom_participant = registration.nom_prenom.upper()
    font_size = 32
    max_text_width = page_width - 60*mm
    while stringWidth(nom_participant, "Helvetica-Bold", font_size) > max_text_width and font_size > 16:
        font_size -= 2

    p.setFillColor(TEXT_DARK)
    p.setFont("Helvetica-Bold", font_size)
    p.drawCentredString(page_width/2, page_height - 87*mm, nom_participant)

    # Soulignement élégant
    p.setStrokeColor(ROSE_COMSAS)
    p.setLineWidth(1)
    p.line(page_width*0.25, page_height - 92*mm, page_width*0.75, page_height - 92*mm)

    # 7. Motif et Description de l'événement
    p.setFillColor(TEXT_DARK)
    p.setFont("Helvetica", 13)
    
    texte_principal = event.certificate_main_text or f"pour sa participation active et remarquable aux travaux de l'événement \"{event.title_fr}\" organisé par le COMSAS."
    
    # Découpage du texte sur plusieurs lignes propres
    mots = texte_principal.split()
    lignes, ligne_en_cours = [], ""
    for mot in mots:
        if stringWidth(ligne_en_cours + " " + mot, "Helvetica", 13) < (page_width - 60*mm):
            ligne_en_cours += (" " + mot if ligne_en_cours else mot)
        else:
            lignes.append(ligne_en_cours)
            ligne_en_cours = mot
    if ligne_en_cours:
        lignes.append(ligne_en_cours)

    y_pos = page_height - 105*mm
    for l in lignes[:3]:
        p.drawCentredString(page_width/2, y_pos, l)
        y_pos -= 6.5*mm

    # 8. Date & Lieu (Bas gauche)
    p.setFont("Helvetica-Oblique", 10)
    p.setFillColor(TEXT_MUTED)
    date_str = timezone.now().strftime('%d/%m/%Y')
    p.drawString(22*mm, 35*mm, f"Fait à Yaoundé, le {date_str}")
    p.setFont("Helvetica", 8)
    p.drawString(22*mm, 30*mm, "Réf. Officielle COMSAS - Faculté des Sciences")

    # 9. Signatures officielles (Centre et droite)
    sig_center_x = page_width/2
    p.setFont("Helvetica-Bold", 11)
    p.setFillColor(TEXT_DARK)
    pres_title = getattr(event, 'certificate_president_title', '') or "Le Président du COMS.A.S"
    p.drawCentredString(sig_center_x, 38*mm, pres_title)

    # Cachet / Signature du président
    sig_path = event.president_signature.path if (getattr(event, 'president_signature', None) and os.path.exists(event.president_signature.path)) else os.path.join(settings.BASE_DIR, 'static', 'images', 'signature.png')
    if os.path.exists(sig_path):
        try:
            p.drawImage(ImageReader(sig_path), sig_center_x - 22*mm, 15*mm, width=44*mm, height=22*mm, mask='auto', preserveAspectRatio=True)
        except Exception:
            pass

    # 10. QR Code de certification d'authenticité (Bas droite)
    qr_taille = 24*mm
    qr_x = page_width - 45*mm
    qr_y = 20*mm
    
    verify_url = f"{getattr(settings, 'SITE_URL', 'https://comsas-uy1.com')}{reverse('ticket_verify', kwargs={'uuid': registration.uuid})}"
    qr = qrcode.QRCode(box_size=6, border=0)
    qr.add_data(verify_url)
    qr.make(fit=True)
    qr_buffer = BytesIO()
    qr.make_image(fill_color="#C2185B", back_color="white").save(qr_buffer, 'PNG')
    qr_buffer.seek(0)
    
    p.drawImage(ImageReader(qr_buffer), qr_x, qr_y, width=qr_taille, height=qr_taille)
    
    p.setFont("Helvetica-Bold", 6.5)
    p.setFillColor(ROSE_DARK)
    p.drawCentredString(qr_x + qr_taille/2, qr_y - 3.5*mm, "CERTIFICAT VÉRIFIABLE")
    p.setFont("Helvetica", 5.5)
    p.setFillColor(TEXT_MUTED)
    p.drawCentredString(qr_x + qr_taille/2, qr_y - 6*mm, str(registration.uuid)[:18])

    p.showPage()
    p.save()

    buffer.seek(0)
    if registration.certificate_pdf:
        registration.certificate_pdf.delete(save=False)
    registration.certificate_pdf.save(f'certificate_{registration.uuid}.pdf', File(buffer), save=True)
    return registration.certificate_pdf.url
