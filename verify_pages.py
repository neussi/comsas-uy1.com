import os
import django
from django.test import Client
from django.urls import reverse
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'comsas_website.settings')
django.setup()

def verify_pages():
    client = Client()
    print("Initializing verification...")
    
    # Setup Data
    from main.models import Event, EventRegistration, GalleryAlbum
    
    # Ensure Event exists
    event = Event.objects.first()
    if not event:
        print("Creating test event...")
        event = Event.objects.create(
             title_fr="Test Event Verification", 
             date_event=timezone.now() + timezone.timedelta(days=10),
             registration_deadline=timezone.now() + timezone.timedelta(days=9),
             location="Amphi 300",
             description_fr="Description test",
             is_active=True
        )
    
    # Ensure Registration exists
    reg = EventRegistration.objects.filter(event=event).first()
    if not reg:
        print("Creating test registration...")
        reg = EventRegistration.objects.create(
            event=event, 
            nom_prenom="Test User", 
            email="test_verification@example.com",
            telephone="600000000",
            promotion="L3"
        )
        # Regenerate ticket to test new design
        from main.utils import generate_ticket
        pdf_url = generate_ticket(reg)
        print(f"Regenerated ticket: {pdf_url}")

    pages = [
        ('home', {}),
        ('gallery', {}),
        ('contact_success', {}),
        ('event_detail', {'pk': event.pk}),
        ('event_registration_success', {'uuid': reg.uuid}),
        ('download_ticket', {'uuid': reg.uuid}),
        ('ticket_verify', {'uuid': reg.uuid}),
    ]
    
    album = GalleryAlbum.objects.first()
    if album:
        pages.append(('gallery_detail', {'pk': album.pk}))
        
    print(f"\nVerifying {len(pages)} pages/actions...")
    all_passed = True
    
    for name, kwargs in pages:
        try:
            url = reverse(name, kwargs=kwargs)
            print(f"Checking {url}...", end=" ")
            response = client.get(url)
            
            if response.status_code in [200, 302]:
                print(f"OK ({response.status_code})")
                if name == 'download_ticket':
                    if response['Content-Type'] == 'application/pdf':
                         print("   -> Correct Content-Type: application/pdf")
                    else:
                         print(f"   -> ERROR: Content-Type is {response['Content-Type']}")
                         all_passed = False
            else:
                print(f"FAILED ({response.status_code})")
                all_passed = False
        except Exception as e:
            print(f"\nEXCEPTION: {name} - {e}")
            all_passed = False
            
    if all_passed:
        print("\n✅ ALL CHECKS PASSED!")
    else:
        print("\n❌ SOME CHECKS FAILED.")

if __name__ == '__main__':
    verify_pages()
