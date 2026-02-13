#!/usr/bin/env python3
"""
Test script to generate a sample certificate
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'comsas_website.settings')
django.setup()

from main.models import Event, EventRegistration
from main.certificate_utils import generate_certificate
from django.utils import timezone

def test_certificate_generation():
    print("="*60)
    print("🎓 Testing Certificate Generation")
    print("="*60)
    
    # Get or create a test event
    event, created = Event.objects.get_or_create(
        title_fr="Séminaire de Maintenance Informatique",
        defaults={
            'title_en': 'IT Maintenance Seminar',
            'description_fr': 'Un séminaire sur la maintenance informatique',
            'description_en': 'A seminar on IT maintenance',
            'date_event': timezone.now() + timezone.timedelta(days=7),
            'location': 'Centre Universitaire des Technologies, UY1',
            'registration_deadline': timezone.now() + timezone.timedelta(days=5),
            'certificate_enabled': True,
            'certificate_title': 'SÉMINAIRE DE MAINTENANCE INFORMATIQUE',
            'certificate_description': """Le computer science association (Club informatique) de l'université de Yaoundé 1 en abrégé COMS.A.S, par la voix de son président, 
certifie que le nommé a participé au séminaire de maintenance informatique tenu du 19 au 20 Novembre
2025 au centre universitaire des technologies et de l'information de cette université et qui avait pour module : maintenance matérielle,
maintenance logicielle et mise en réseau des ordinateurs. Ce dernier a démontré un engagement sérieux dans l'apprentissage des technologies et
des connaissances abordées. En foi de quoi la présente attestation est établie pour lui valoir ce que de droit.""",
            'certificate_president_name': 'MFENJOU ANAS CHERIF',
            'certificate_president_title': 'Président du COMS.A.S',
            'certificate_dept_head_name': 'AMINOU HALINOU',
            'certificate_dept_head_title': 'Chef de département informatique',
        }
    )
    
    if created:
        print(f"✅ Created test event: {event.title_fr}")
    else:
        print(f"📋 Using existing event: {event.title_fr}")
    
    # Get or create a test registration
    registration, created = EventRegistration.objects.get_or_create(
        event=event,
        email='donkam.ruth@example.com',
        defaults={
            'nom_prenom': 'Donkam Ruth Samanza',
            'telephone': '+237 6 XX XX XX XX',
            'promotion': 'Licence 3',
            'is_confirmed': True,
        }
    )
    
    if created:
        print(f"✅ Created test registration for: {registration.nom_prenom}")
    else:
        print(f"📋 Using existing registration for: {registration.nom_prenom}")
    
    # Generate certificate
    print("\n🎨 Generating certificate...")
    try:
        cert_url = generate_certificate(registration)
        print(f"✅ Certificate generated successfully!")
        print(f"📄 PDF saved to: {registration.certificate_pdf.path}")
        print(f"🔗 URL: {cert_url}")
        
        # Check file size
        import os
        file_size = os.path.getsize(registration.certificate_pdf.path)
        print(f"📊 File size: {file_size / 1024:.2f} KB")
        
    except Exception as e:
        print(f"❌ Error generating certificate: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("✅ Test completed!")
    print("="*60)

if __name__ == '__main__':
    test_certificate_generation()
