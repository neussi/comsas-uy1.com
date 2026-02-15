
import os
import django
from django.conf import settings
from django.utils import timezone

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'comsas_website.settings')
django.setup()

from main.models import Event, EventRegistration
from main.badge_utils import generate_badge

def test_badge_generation():
    print("=" * 60)
    print("🎓 Testing Badge Generation")
    print("=" * 60)
    
    # 1. Get or Create Test Event
    event, created = Event.objects.get_or_create(
        title_fr="Séminaire de Maintenance Informatique",
        defaults={
            'description_fr': "Séminaire pratique sur la maintenance.",
            'date_event': timezone.now() + timezone.timedelta(days=10),
            'location': "CUTI",
            'registration_deadline': timezone.now() + timezone.timedelta(days=5),
            'badge_enabled': True,
        }
    )
    
    if created:
        print(f"🆕 Created new event: {event.title_fr}")
    else:
        print(f"📋 Using existing event: {event.title_fr}")
        # Ensure badges enabled
        event.badge_enabled = True
        event.save()
        
    # 2. Get or Create Test Registration
    registration, created = EventRegistration.objects.get_or_create(
        event=event,
        email="donkam.ruth@example.com",
        defaults={
            'nom_prenom': "Donkam Ruth Samanza",
            'telephone': "612345678",
            'promotion': "L3 INFO",
            'is_confirmed': True
        }
    )
    
    if created:
        print(f"🆕 Created new registration: {registration.nom_prenom}")
    else:
        print(f"📋 Using existing registration for: {registration.nom_prenom}")
        # Ensure confirmed
        if not registration.is_confirmed:
            registration.is_confirmed = True
            registration.save()
            print("✅ Registration confirmed.")
            
    # 3. Generate Badge
    print("\n🎨 Generating badge...")
    try:
        url = generate_badge(registration)
        if url:
            print("✅ Badge generated successfully!")
            print(f"📄 PDF saved to: {registration.badge_pdf.path}")
            print(f"🔗 URL: {url}")
            print(f"📊 File size: {os.path.getsize(registration.badge_pdf.path) / 1024:.2f} KB")
        else:
            print("❌ Failed to generate badge (returned None). Check if badges enabled.")
    except Exception as e:
        print(f"❌ Error generating badge: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("✅ Test completed!")
    print("=" * 60)

if __name__ == "__main__":
    test_badge_generation()
