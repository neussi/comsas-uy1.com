
import os
import django
from io import BytesIO

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aaelbm2_website.settings')
django.setup()

from main.models import Member
from main.utils import generate_member_card
from django.core.mail import send_mail, EmailMessage
from django.conf import settings

def debug_card():
    # Create or get a dummy member for testing
    member = Member.objects.filter(email='neussi344@gmail.com').first()
    if not member:
        member = Member.objects.create(
            email='neussi344@gmail.com',
            nom_prenom='Test User For Card',
            matricule='CM-TEST-001',
            promotion=2024,
            is_active=True,
            member_type='simple',
            profession='Developer'
        )
    
    print(f"Testing card generation for: {member.nom_prenom}")
    
    try:
        # Check signature path
        sig_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'signature.png')
        print(f"Checking Signature Path: {sig_path} -> Exists? {os.path.exists(sig_path)}")

        # Generate PDF
        print("Generating PDF buffer...")
        pdf_buffer = generate_member_card(member)
        print(f"PDF Generated. Size: {len(pdf_buffer.getvalue())} bytes")
        
        # Save locally to inspect
        with open('final_card_test.pdf', 'wb') as f:
            f.write(pdf_buffer.getvalue())
        print("Saved final_card_test.pdf")
        
        # Test Email Sending Logic
        print("Attempting to send email...")
        email = EmailMessage(
            "Votre Carte COMSAS (Ajustement Vertical v2)",
            "Voici votre carte avec le titre rabaissé encore un peu.",
            settings.DEFAULT_FROM_EMAIL,
            [member.email],
        )
        email.attach('card.pdf', pdf_buffer.getvalue(), 'application/pdf')
        email.send(fail_silently=False)
        print("Email Sent Successfully")

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    debug_card()
