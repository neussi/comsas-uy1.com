import os
import django
import sys
from django.utils import timezone
from django.core.files import File
from io import BytesIO

# Setup Django
sys.path.append('/home/npe-tech/Projets/Comsas')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'comsas_website.settings')
django.setup()

from main.models import Event, EventRegistration
from main.certificate_utils import generate_certificate
from main.badge_utils import generate_badge
from main.utils import generate_ticket
from django.conf import settings

def generate_full_poc():
    title = "SYMPOSIUM INTERNATIONAL SUR L'IA ET LA CYBERSÉCURITÉ - ÉDITION 2026"
    
    # 1. Mock Partner Logos (Using local images)
    partner_logo_path = os.path.join(settings.BASE_DIR, 'static/images/comsas.png') # Using static logo as placeholder
    
    # 2. Create/Update Event
    event, created = Event.objects.get_or_create(
        title_fr=title,
        defaults={
            'date_event': timezone.now() + timezone.timedelta(days=15),
            'registration_deadline': timezone.now() + timezone.timedelta(days=10),
            'location': "Centre Universitaire des Technologies, Yaoundé",
            'is_active': True,
            'certificate_title': "ATTESTATION DE PARTICIPATION ET D'EXCELLENCE",
            'certificate_president_name': "Borel Henri NGUIMEZAP",
            'certificate_president_title': "Président du COMS.A.S",
            'certificate_main_text': "Le COMSAS, par la voix de son président, certifie que le participant a suivi avec succès les ateliers pratiques de cybersécurité offensive et de défense périmétrique lors de ce symposium international.",
            'badge_enabled': True,
        }
    )
    
    # Add partner logos
    if os.path.exists(partner_logo_path):
        with open(partner_logo_path, 'rb') as f:
            logo_file = File(f)
            event.partner_logo_1.save('partner1.png', logo_file, save=False)
            event.partner_logo_2.save('partner2.png', logo_file, save=False)
            event.partner_logo_3.save('partner3.png', logo_file, save=True)

    # 3. Create Participant
    reg, _ = EventRegistration.objects.get_or_create(
        email="expert_tech@comsas.org",
        event=event,
        defaults={
            'nom_prenom': "PATRICE NGUEKAM DASSI",
            'promotion': "Master 2 - Sécurité Informatique",
            'is_confirmed': True,
        }
    )

    print(f"--- Generating Previews for: {title} ---")
    
    # 4. Generate Certificate
    cert_url = generate_certificate(reg)
    print(f"✅ Certificate: {cert_url}")
    
    # 5. Generate Badge
    badge_url = generate_badge(reg)
    print(f"✅ Badge: {badge_url}")
    
    # 6. Generate Ticket
    ticket_url = generate_ticket(reg)
    print(f"✅ Ticket: {ticket_url}")
    
    return reg

if __name__ == "__main__":
    registration = generate_full_poc()
    print("\nExtraction des fichiers PDF pour visualisation...")
    
    # Copy files to a accessible location for viewing
    import shutil
    media_root = settings.MEDIA_ROOT
    target_dir = os.path.join(settings.BASE_DIR, 'preview_docs')
    os.makedirs(target_dir, exist_ok=True)
    
    if registration.certificate_pdf:
        shutil.copy(registration.certificate_pdf.path, os.path.join(target_dir, 'preview_certificate.pdf'))
    if registration.badge_pdf:
        shutil.copy(registration.badge_pdf.path, os.path.join(target_dir, 'preview_badge.pdf'))
    if registration.ticket_pdf:
        shutil.copy(registration.ticket_pdf.path, os.path.join(target_dir, 'preview_ticket.pdf'))
    
    print(f"Previsualisation disponible dans: {target_dir}")
