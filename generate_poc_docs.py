import os
import django
import sys

# Setup Django
sys.path.append('/home/npe-tech/Projets/Comsas')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'comsas_website.settings')
django.setup()

from main.models import Event, EventRegistration
from main.certificate_utils import generate_certificate
from main.badge_utils import generate_badge
from main.utils import generate_ticket
from django.utils import timezone
from django.core.files.base import ContentFile
import uuid

def generate_poc():
    title = "Grand Sommet International de l'Innovation Technologique et de l'Intelligence Artificielle en Afrique Centrale 2026"
    
    # 1. Ensure event exists with all required fields
    event = Event.objects.filter(title_fr=title).first()
    if not event:
        event = Event.objects.create(
            title_fr=title,
            date_event=timezone.now() + timezone.timedelta(days=7),
            registration_deadline=timezone.now() + timezone.timedelta(days=6),
            location='Palais des Congrès, Yaoundé',
            certificate_enabled=True,
            badge_enabled=True,
            certificate_title="ATTESTATION DE PARTICIPATION D'EXCELLENCE",
            certificate_main_text="pour avoir brillamment participé et contribué aux travaux de recherche lors de cet événement d'envergure internationale.",
        )
    
    # 2. Create a dummy registration
    email = "poc_tester@example.com"
    registration = EventRegistration.objects.filter(email=email, event=event).first()
    if not registration:
        registration = EventRegistration.objects.create(
            email=email,
            event=event,
            nom_prenom="JEAN PATRICE NGUEKAM DASSI",
            promotion="Niveau 4 - Génie Logiciel",
            is_confirmed=True,
        )
    
    print(f"Generating documents for Event: {event.title_fr}")
    
    # 3. Generate Certificate
    cert_url = generate_certificate(registration)
    print(f"Certificate generated at: {cert_url}")
    
    # 4. Generate Badge
    badge_url = generate_badge(registration)
    print(f"Badge generated at: {badge_url}")
    
    # 5. Generate Ticket
    ticket_url = generate_ticket(registration)
    print(f"Ticket generated at: {ticket_url}")
    
    return cert_url, badge_url, ticket_url

if __name__ == "__main__":
    cert, badge, ticket = generate_poc()
    print("\n--- POC Results ---")
    print(f"Certificate: {cert}")
    print(f"Badge: {badge}")
    print(f"Ticket: {ticket}")
