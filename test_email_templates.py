#!/usr/bin/env python3
"""
Test script to verify HTML email templates are working correctly.
This will send test emails using the console backend.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'comsas_website.settings')
django.setup()

from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils import timezone

def test_contact_notification():
    """Test contact notification email"""
    print("\n📧 Testing Contact Notification Email...")
    
    html_content = render_to_string('emails/contact_notification.html', {
        'nom_prenom': 'Jean Dupont',
        'email': 'jean.dupont@example.com',
        'sujet': 'Question sur l\'adhésion',
        'message': 'Bonjour, je souhaiterais avoir plus d\'informations sur les modalités d\'adhésion à COMS.A.S.',
        'date_envoi': timezone.now(),
    })
    
    email = EmailMultiAlternatives(
        'Nouveau message de contact - Question sur l\'adhésion',
        'Version texte du message',
        settings.EMAIL_HOST_USER,
        ['admin@comsas.com'],
    )
    email.attach_alternative(html_content, "text/html")
    email.send()
    print("✅ Contact notification email sent!")

def test_event_registration():
    """Test event registration confirmation email"""
    print("\n🎉 Testing Event Registration Email...")
    
    html_content = render_to_string('emails/event_registration_confirmation.html', {
        'participant_name': 'Marie Kamga',
        'event_title': 'Conférence sur l\'IA et le Machine Learning',
        'event_date': timezone.now() + timezone.timedelta(days=7),
        'event_location': 'Amphi 300, Université de Yaoundé 1',
    })
    
    email = EmailMultiAlternatives(
        'Confirmation inscription - Conférence IA',
        'Version texte du message',
        settings.EMAIL_HOST_USER,
        ['marie.kamga@example.com'],
    )
    email.attach_alternative(html_content, "text/html")
    email.send()
    print("✅ Event registration email sent!")

def test_member_card():
    """Test member card email"""
    print("\n🎊 Testing Member Card Email...")
    
    html_content = render_to_string('emails/member_card_email.html', {
        'member_name': 'Paul Nkeng',
        'matricule': 'COMS2024001',
        'member_type': 'Membre Simple',
        'date_adhesion': timezone.now(),
    })
    
    email = EmailMultiAlternatives(
        'Votre Carte de Membre COMS.A.S',
        'Version texte du message',
        settings.EMAIL_HOST_USER,
        ['paul.nkeng@example.com'],
    )
    email.attach_alternative(html_content, "text/html")
    email.send()
    print("✅ Member card email sent!")

def test_admin_access():
    """Test admin access confirmation email"""
    print("\n✅ Testing Admin Access Confirmation Email...")
    
    html_content = render_to_string('emails/admin_access_confirmation.html', {
        'first_name': 'Sophie',
        'username': 'sophie.admin',
        'requested_role': 'Modérateur',
        'date_demande': timezone.now(),
    })
    
    email = EmailMultiAlternatives(
        'Demande d\'accès reçue - COMS.A.S',
        'Version texte du message',
        settings.EMAIL_HOST_USER,
        ['sophie@example.com'],
    )
    email.attach_alternative(html_content, "text/html")
    email.send()
    print("✅ Admin access confirmation email sent!")

if __name__ == '__main__':
    print("="*60)
    print("🧪 Testing HTML Email Templates")
    print("="*60)
    
    test_contact_notification()
    test_event_registration()
    test_member_card()
    test_admin_access()
    
    print("\n" + "="*60)
    print("✅ All email templates tested successfully!")
    print("="*60)
    print("\n💡 Check your console for the rendered emails.")
