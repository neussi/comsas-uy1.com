"""
Tests complets de l'intégration Propenta Pay V2
Vérifie le client API, la signature HMAC, les processeurs de paiements et les webhooks
"""
import os
import sys
import json
import time
import hmac
import hashlib
from decimal import Decimal
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'comsas_website.settings')
django.setup()

from django.test import Client, TestCase
from django.utils import timezone
from main.models import (
    SponsorshipSession, Mentor, Mentee, Match,
    Event, EventActivity, EventActivityApplication,
    Contest, Candidate, Vote, CofestiEdition, CofestiCandidate, CofestiVote,
    Donation
)
from main.propenta_service import (
    PropentaPayAPIClient,
    PropentaPaymentProcessor,
    PropentaWebhookHandler
)

def run_tests():
    print("=" * 70)
    print(" DÉBUT DES TESTS COMPLETS PROPENTA PAY V2")
    print("=" * 70)

    # -------------------------------------------------------------------------
    # 1. TEST DU CLIENT PROPENTA & SIGNATURE HMAC
    # -------------------------------------------------------------------------
    print("\n--- [TEST 1] Client API & Signature HMAC ---")
    client = PropentaPayAPIClient()
    assert bool(client.client_id), "Client ID non configuré"
    assert bool(client.client_secret), "Client Secret non configuré"

    # Test normalisation téléphone
    assert client.normalize_phone("+237699112233") == "237699112233"
    assert client.normalize_phone("677889900") == "237677889900"
    assert client.normalize_phone("237699001122") == "237699001122"
    print("  ✓ Normalisation des numéros de téléphone validée")

    # Test détection d'opérateur
    assert client.detect_payment_method("699112233") == "ORANGE_MONEY"
    assert client.detect_payment_method("656001122") == "ORANGE_MONEY"
    assert client.detect_payment_method("677889900") == "MTN_MOMO"
    assert client.detect_payment_method("652001122") == "MTN_MOMO"
    print("  ✓ Détection Orange Money / MTN MoMo validée")

    # Test de signature HMAC
    body = json.dumps({"order_id": "TEST-123", "amount": 5000}).encode('utf-8')
    sig_header = client.sign_request("POST", "/payin", body)
    assert sig_header.startswith("t="), "Format signature invalide"
    assert ",v1=" in sig_header, "Format signature v1 manquant"
    print(f"  ✓ Signature HMAC calculée avec succès: {sig_header[:40]}...")

    # -------------------------------------------------------------------------
    # 2. TEST DU PROCESSUS DE PARRAINAGE PROFESSIONNEL (5 000 F / 10 000 F)
    # -------------------------------------------------------------------------
    print("\n--- [TEST 2] Parrainage Professionnel (Propenta Pay) ---")
    session, _ = SponsorshipSession.objects.get_or_create(
        name="Session Test 2026",
        defaults={
            'is_active': True,
            'start_date': timezone.now().date(),
            'end_date': timezone.now().date() + timezone.timedelta(days=60),
        }
    )

    # Création d'un Parrain (5 000 FCFA)
    mentor = Mentor.objects.create(
        session=session,
        first_name="Alain",
        last_name="Tech",
        email=f"alain.tech.{int(time.time())}@example.com",
        phone="237699001122",
        cycle="master",
        level="master_2",
        filiere_option="GL",
        profession="DevOps Engineer",
        years_of_experience=5,
        skills_with_levels="Docker (Expert), Python (Avancé)",
        amount=Decimal('5000.00'),
        transaction_id=f"SPONSORPAY-PARRAIN-TEST-{int(time.time())}",
        payment_status='pending',
        is_paid=False
    )

    # Création d'un Filleul (10 000 FCFA)
    mentee = Mentee.objects.create(
        session=session,
        first_name="Clarisse",
        last_name="Dev",
        email=f"clarisse.dev.{int(time.time())}@example.com",
        phone="237677112233",
        cycle="licence",
        level="licence_3",
        filiere_option="GL",
        desired_specialty="DevOps",
        skills_to_acquire="Docker, Linux",
        desired_mentor_type="Senior DevOps",
        amount=Decimal('10000.00'),
        transaction_id=f"SPONSORPAY-FILLEUL-TEST-{int(time.time())}",
        payment_status='pending',
        is_paid=False
    )

    processor = PropentaPaymentProcessor()

    # Confirmation manuelle / par webhook
    res_mentor = processor.confirm_sponsorship_payment(mentor, payment_ref="PI-TEST-MENTOR")
    mentor.refresh_from_db()
    assert mentor.is_paid == True, "Mentor devrait être marqué payé"
    assert mentor.payment_status == 'confirmed', "Statut devrait être confirmed"
    assert mentor.qr_code is not None, "QR code manquant"
    print(f"  ✓ Parrain validé: {mentor.first_name} {mentor.last_name} | UUID: {mentor.uuid}")

    res_mentee = processor.confirm_sponsorship_payment(mentee, payment_ref="PI-TEST-MENTEE")
    mentee.refresh_from_db()
    assert mentee.is_paid == True, "Mentee devrait être marquée payée"
    assert mentee.payment_status == 'confirmed', "Statut mentee confirmed"
    print(f"  ✓ Filleul validé: {mentee.first_name} {mentee.last_name} | UUID: {mentee.uuid}")

    # Test d'idempotence (confirmer une 2ème fois ne doit rien casser)
    res_mentor_2 = processor.confirm_sponsorship_payment(mentor)
    assert res_mentor_2.get('success') == True, "Idempotence échouée"
    print("  ✓ Idempotence validée pour le parrainage")

    # -------------------------------------------------------------------------
    # 3. TEST ACTIVITÉ D'ÉVÉNEMENT (EventActivityApplication)
    # -------------------------------------------------------------------------
    print("\n--- [TEST 3] Activités d'événements (Propenta Pay) ---")
    event = Event.objects.first()
    if not event:
        event = Event.objects.create(
            title_fr="COFESTI 2026 Test",
            date_event=timezone.now().date(),
            location='Amphi 502',
            is_active=True
        )
    activity, _ = EventActivity.objects.get_or_create(
        event=event,
        title="Tournoi Football Test",
        defaults={
            'slug': 'tournoi-football-test',
            'activity_type': 'team',
            'date_activity': timezone.now(),
            'max_participants': 50,
            'price': Decimal('2000.00'),
            'is_active': True
        }
    )

    app = EventActivityApplication.objects.create(
        activity=activity,
        full_name="Capitaine Test",
        email=f"cap.{int(time.time())}@example.com",
        phone="237699112233",
        team_name="Les Aigles",
        amount=activity.price,
        transaction_id=f"ACTIVITYPAY-TEST-{int(time.time())}",
        status='pending',
        is_paid=False
    )

    res_app = processor.confirm_activity_payment(app)
    app.refresh_from_db()
    assert app.is_paid == True, "Candidature activité non payée"
    assert app.status == 'confirmed', "Statut activité non confirmé"
    print(f"  ✓ Activité validée: {app.activity.title} pour {app.full_name}")

    # -------------------------------------------------------------------------
    # 4. TEST DES WEBHOOKS PROPENTA PAY (HTTP POST sur /webhook)
    # -------------------------------------------------------------------------
    print("\n--- [TEST 4] Webhooks Propenta Pay (Route /webhook) ---")
    c = Client()

    # Webhook pour Parrain
    webhook_payload_mentor = {
        "event": "transaction.status",
        "data": {
            "transactionRef": "PI-WH-9999",
            "order_id": mentor.transaction_id,
            "status": "SUCCESS",
            "amount": 5000,
            "phone": mentor.phone,
            "externalTxId": "TX-12345"
        }
    }
    response = c.post(
        '/webhook',
        data=json.dumps(webhook_payload_mentor),
        content_type='application/json'
    )
    assert response.status_code == 200, f"Webhook /webhook a échoué: {response.status_code}"
    print(f"  ✓ POST /webhook reçu et traité avec succès (HTTP {response.status_code})")

    # Webhook avec slash /webhook/
    response_slash = c.post(
        '/webhook/',
        data=json.dumps(webhook_payload_mentor),
        content_type='application/json'
    )
    assert response_slash.status_code == 200, f"Webhook /webhook/ a échoué: {response_slash.status_code}"
    print(f"  ✓ POST /webhook/ reçu et traité avec succès (HTTP {response_slash.status_code})")

    # Webhook API /api/propenta/webhook/
    response_api = c.post(
        '/api/propenta/webhook/',
        data=json.dumps(webhook_payload_mentor),
        content_type='application/json'
    )
    assert response_api.status_code == 200, f"Webhook /api/propenta/webhook/ a échoué: {response_api.status_code}"
    print(f"  ✓ POST /api/propenta/webhook/ reçu et traité avec succès (HTTP {response_api.status_code})")

    # -------------------------------------------------------------------------
    # 5. TEST DE PAIEMENT ÉCHOUÉ / ANNULÉ VIA WEBHOOK
    # -------------------------------------------------------------------------
    print("\n--- [TEST 5] Traitement des échecs de transaction via Webhook ---")
    failed_mentee = Mentee.objects.create(
        session=session,
        first_name="Echec",
        last_name="Test",
        email=f"echec.{int(time.time())}@example.com",
        phone="237677112233",
        cycle="licence",
        level="licence_1",
        filiere_option="GL",
        desired_specialty="DevOps",
        skills_to_acquire="Docker",
        amount=Decimal('10000.00'),
        transaction_id=f"SPONSORPAY-FILLEUL-FAIL-{int(time.time())}",
        payment_status='pending',
        is_paid=False
    )
    webhook_payload_fail = {
        "event": "transaction.status",
        "data": {
            "transactionRef": "PI-FAIL-001",
            "order_id": failed_mentee.transaction_id,
            "status": "FAILED",
            "amount": 10000,
            "phone": failed_mentee.phone
        }
    }
    response_fail = c.post('/webhook', data=json.dumps(webhook_payload_fail), content_type='application/json')
    assert response_fail.status_code == 200
    failed_mentee.refresh_from_db()
    assert failed_mentee.is_paid == False, "Ne doit pas être payé"
    assert failed_mentee.payment_status == 'failed', "Statut doit être failed"
    print("  ✓ Échec de paiement traité correctement par le Webhook (is_paid=False, payment_status='failed')")

    print("\n" + "=" * 70)
    print(" TOUS LES TESTS PROPENTA PAY V2 SONT VALIDÉS AVEC SUCCÈS (100%)")
    print("=" * 70)

if __name__ == '__main__':
    run_tests()
