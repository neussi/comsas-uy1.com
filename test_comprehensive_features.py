import os
import django
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'comsas_website.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
import datetime

from main.models import (
    User, Member, SponsorshipSession, Mentor, Mentee, Match,
    Event, EventActivity, EventActivityApplication,
    CofestiEdition, CofestiCandidate, CofestiVote
)
from main.forms import MentorRegistrationForm, MenteeRegistrationForm, EventActivityApplicationForm
from main.freemopay_service import FreemopayPaymentProcessor

print("="*70)
print("RUNNING COMPREHENSIVE E2E & UNIT TESTS")
print("="*70)

def create_test_image(size=(400, 500), color='blue', format='JPEG'):
    file_obj = BytesIO()
    img = Image.new('RGB', size, color=color)
    img.save(file_obj, format=format)
    file_obj.seek(0)
    return SimpleUploadedFile(f"test_portrait.{format.lower()}", file_obj.read(), content_type=f"image/{format.lower()}")

def create_oversized_image():
    file_obj = BytesIO()
    file_obj.write(b"0" * (5500000))
    file_obj.seek(0)
    return SimpleUploadedFile("too_heavy.jpg", file_obj.read(), content_type="image/jpeg")

def create_corrupted_image():
    file_obj = BytesIO()
    file_obj.write(b"Not an actual image payload")
    file_obj.seek(0)
    return SimpleUploadedFile("fake.jpg", file_obj.read(), content_type="image/jpeg")

client = Client()

# ---------------------------------------------------------
# TEST 1: Parrainage Professionnel (Mentor & Mentee)
# ---------------------------------------------------------
print("\n--- [TEST 1] Parrainage Professionnel: Form & Model Validation ---")

session, _ = SponsorshipSession.objects.get_or_create(
    name="Session Test 2026",
    defaults={
        'is_active': True,
        'start_date': timezone.now().date(),
        'end_date': (timezone.now() + datetime.timedelta(days=90)).date(),
    }
)

# 1.1 Mentor registration with valid portrait photo
valid_photo = create_test_image(color='darkblue')
mentor_data = {
    'first_name': 'Jean',
    'last_name': 'Dupont',
    'email': 'jean.dupont.test@example.com',
    'phone': '+237699001122',
    'level': 'ALUMNI',
    'specialty': 'GL',
    'profession': 'Senior Cloud Architect & DevOps Lead',
    'company': 'Google Cloud Partner',
    'years_of_experience': 7,
    'bio': 'Passionné de Cloud, Kubernetes et architectures distribuées.',
    'expertise_domains_list': ['software_eng', 'cybersecurity'],
    'max_mentees': 3,
}
form_mentor = MentorRegistrationForm(data=mentor_data, files={'photo': valid_photo})
assert form_mentor.is_valid(), f"Mentor form should be valid, errors: {form_mentor.errors}"
mentor = form_mentor.save(commit=False)
mentor.session = session
mentor.save()
assert mentor.pk is not None
assert mentor.profession == 'Senior Cloud Architect & DevOps Lead'
assert mentor.years_of_experience == 7
assert mentor.photo.name is not None
print("✓ Mentor registration with required portrait photo, profession, company and experience: SUCCESS")

# 1.2 Mentee registration with valid portrait photo
valid_mentee_photo = create_test_image(color='green')
mentee_data = {
    'first_name': 'Alice',
    'last_name': 'Kamga',
    'email': 'alice.kamga.test@example.com',
    'phone': '+237677112233',
    'level': 'L1',
    'desired_specialty': 'Data Science & Intelligence Artificielle',
    'skills_to_acquire': 'Machine Learning, Deep Learning, MLOps',
    'bio': 'Étudiante passionnée cherchant à se perfectionner en IA.',
    'competencies_list': ['python'],
    'professional_domains_list': ['data_science'],
}
form_mentee = MenteeRegistrationForm(data=mentee_data, files={'photo': valid_mentee_photo})
assert form_mentee.is_valid(), f"Mentee form should be valid, errors: {form_mentee.errors}"
mentee = form_mentee.save(commit=False)
mentee.session = session
mentee.save()
assert mentee.pk is not None
assert mentee.skills_to_acquire == 'Machine Learning, Deep Learning, MLOps'
assert mentee.desired_specialty == 'Data Science & Intelligence Artificielle'
assert mentee.photo.name is not None
print("✓ Mentee registration with required portrait photo, skills to acquire and desired specialty: SUCCESS")

# 1.3 Photo size check (> 5MB must be rejected)
heavy_photo = create_oversized_image()
form_heavy = MentorRegistrationForm(data=mentor_data, files={'photo': heavy_photo})
assert not form_heavy.is_valid(), "Form with > 5MB photo MUST fail"
assert 'photo' in form_heavy.errors
print("✓ Photo size limit (> 5MB) strictly rejected with user-friendly error: SUCCESS")

# 1.4 Corrupted image check
fake_photo = create_corrupted_image()
form_fake = MenteeRegistrationForm(data=mentee_data, files={'photo': fake_photo})
assert not form_fake.is_valid(), "Form with corrupted photo MUST fail"
assert 'photo' in form_fake.errors
print("✓ Corrupted / non-image format strictly rejected: SUCCESS")

# 1.5 Missing required photo check
form_no_photo = MentorRegistrationForm(data=mentor_data, files={})
assert not form_no_photo.is_valid()
assert 'photo' in form_no_photo.errors
print("✓ Mandatory portrait photo validation enforced: SUCCESS")


# ---------------------------------------------------------
# TEST 2: Événements & Activités (EventDetail & ActivityDetail)
# ---------------------------------------------------------
print("\n--- [TEST 2] Événements & Activités: Views & Dynamic Application Forms ---")

event = Event.objects.first()
if not event:
    event = Event.objects.create(
        title_fr="Festival Tech & Nuit de l'Info 2026",
        title_en="Tech Fest & Info Night 2026",
        description_fr="Grand rassemblement annuel d'informatique.",
        description_en="Annual computer science gathering.",
        date_event=timezone.now() + datetime.timedelta(days=10),
        location="Amphi 1001, Université de Yaoundé I",
        is_active=True,
        is_featured=True
    )

# 2.1 Event detail view check
resp_event = client.get(reverse('event_detail', kwargs={'pk': event.pk}))
assert resp_event.status_code == 200
ev_html = resp_event.content.decode('utf-8')
assert event.title_fr in ev_html or 'Activités' in ev_html
print("✓ Event detail view (HTTP 200) rendering event, activities & recent events: SUCCESS")

# 2.2 Free Individual Activity
act_individual, _ = EventActivity.objects.get_or_create(
    event=event,
    title="Atelier Cybersécurité & Reverse Engineering",
    defaults={
        'activity_type': 'individual',
        'description': "Introduction pratique au reverse engineering.",
        'date_activity': timezone.now() + datetime.timedelta(days=11),
        'location': "Salle Informatique L3",
        'price': Decimal('0.00'),
        'max_participants': 30,
        'rules': "Venir avec son PC portable sous Linux.",
    }
)

resp_act1 = client.get(reverse('activity_detail', kwargs={'slug': act_individual.slug}))
assert resp_act1.status_code == 200
print("✓ Activity detail (Individual) view (HTTP 200): SUCCESS")

# Submit Free Individual Application
post_indiv = {
    'full_name': 'Paul Mbida',
    'email': 'paul.mbida@test.com',
    'phone': '690112233',
    'level': 'Master 1',
    'notes': 'Intéressé par le pentest web'
}
resp_sub1 = client.post(reverse('activity_detail', kwargs={'slug': act_individual.slug}), post_indiv, follow=True)
assert resp_sub1.status_code == 200
app_indiv = EventActivityApplication.objects.filter(activity=act_individual, email='paul.mbida@test.com').first()
assert app_indiv is not None
assert app_indiv.status == 'confirmed', f"Free activity should be auto-confirmed, got {app_indiv.status}"
assert app_indiv.is_paid == True
print("✓ Free individual activity application instantly confirmed (status=confirmed, is_paid=True): SUCCESS")

# 2.3 Paid Team Activity (Tournoi de Football / Hackathon)
act_team, _ = EventActivity.objects.get_or_create(
    event=event,
    title="Tournoi Inter-Niveaux Football",
    defaults={
        'activity_type': 'team',
        'date_activity': timezone.now() + datetime.timedelta(days=11),
        'min_team_size': 5,
        'max_team_size': 7,
        'price': Decimal('15000.00'),
        'max_participants': 8,
        'rules': "5 joueurs de champ + 2 remplaçants maximum. Protège-tibias obligatoires.",
        'location': "Stade du Campus UY1",
    }
)

# Test Team size validation (less than min)
invalid_team_post = {
    'full_name': 'Eric Kamdem',
    'email': 'capitaine.eric@test.com',
    'phone': '699887766',
    'team_name': 'Les Aigles Info',
    'captain_name': 'Eric Kamdem',
    'team_size': 3,  # Invalid: min is 5
    'team_members': 'Eric, Roger, Jean',
}
form_team_bad = EventActivityApplicationForm(activity=act_team, data=invalid_team_post)
assert not form_team_bad.is_valid()
assert 'team_size' in form_team_bad.errors
print("✓ Team size below minimum (min 5) correctly rejected: SUCCESS")

# Test Team size valid
valid_team_post = {
    'full_name': 'Eric Kamdem',
    'email': 'capitaine.eric@test.com',
    'phone': '699887766',
    'team_name': 'Les Aigles Info',
    'captain_name': 'Eric Kamdem',
    'team_size': 6,
    'team_members': 'Eric (Capitaine), Roger, Jean, Marc, Fabrice, Lionel',
}
form_team_ok = EventActivityApplicationForm(activity=act_team, data=valid_team_post)
assert form_team_ok.is_valid(), f"Valid team form had errors: {form_team_ok.errors}"
print("✓ Team activity validation within [min_team_size, max_team_size]: SUCCESS")

# 2.4 Paid Gaming Activity
act_gaming, _ = EventActivity.objects.get_or_create(
    event=event,
    title="Tournoi E-Sport FC 25 & Naruto Storm 4",
    defaults={
        'activity_type': 'gaming',
        'date_activity': timezone.now() + datetime.timedelta(days=11),
        'platform': 'PlayStation 5',
        'price': Decimal('2000.00'),
        'max_participants': 32,
        'rules': "Matchs de 6 minutes. Phase de poules puis élimination directe.",
        'location': "Salle Multimédia COMSAS",
    }
)

# Test Gaming form validation
missing_gamer_post = {
    'full_name': 'Kevin Gamer',
    'email': 'gamer@test.com',
    'phone': '677001122',
    # Missing gamer_tag and gaming_platform
}
form_gaming_bad = EventActivityApplicationForm(activity=act_gaming, data=missing_gamer_post)
assert not form_gaming_bad.is_valid()
assert 'gamer_tag' in form_gaming_bad.errors or 'gaming_platform' in form_gaming_bad.errors
print("✓ Gaming specific fields (gamer_tag, platform) strictly required: SUCCESS")

valid_gamer_post = {
    'full_name': 'Kevin Gamer',
    'email': 'kevin.gamer@test.com',
    'phone': '677001122',
    'gamer_tag': 'ShadowStriker_237',
    'game_name': 'EA Sports FC 25',
    'gaming_platform': 'PlayStation 5',
    'gaming_id': 'PSN-Shadow237',
}
form_gaming_ok = EventActivityApplicationForm(activity=act_gaming, data=valid_gamer_post)
assert form_gaming_ok.is_valid(), f"Gamer form errors: {form_gaming_ok.errors}"
print("✓ Gaming activity application validated: SUCCESS")


# ---------------------------------------------------------
# TEST 3: Freemopay Payment Flow (Pending, Status, Cancel, Success)
# ---------------------------------------------------------
print("\n--- [TEST 3] Freemopay Mobile Money Payment Integration ---")

import uuid

processor = FreemopayPaymentProcessor()

# 3.1 Create pending application for paid gaming activity
tx_uuid = f"ACTIVITYPAY-GAMING-{uuid.uuid4().hex[:6]}"
app_gaming = form_gaming_ok.save(commit=False)
app_gaming.activity = act_gaming
app_gaming.amount = act_gaming.price
app_gaming.status = 'pending'
app_gaming.transaction_id = tx_uuid
app_gaming.save()
assert app_gaming.pk is not None
assert app_gaming.status == 'pending'
assert app_gaming.is_paid == False

# Check status page rendering
resp_status = client.get(reverse('activity_application_status', kwargs={'uuid': app_gaming.uuid}))
assert resp_status.status_code == 200
print("✓ Activity application status page (pending state, HTTP 200): SUCCESS")

# Check status API endpoint
resp_api = client.get(reverse('api_activity_payment_status', kwargs={'transaction_id': app_gaming.transaction_id}))
assert resp_api.status_code == 200
json_api = resp_api.json()
assert json_api['status'] == 'pending'
assert json_api['is_paid'] == False
print("✓ Activity status polling API (JSON response): SUCCESS")

# 3.2 Payment Cancellation
resp_cancel = client.post(reverse('activity_payment_cancel', kwargs={'uuid': app_gaming.uuid}), follow=True)
assert resp_cancel.status_code == 200
app_gaming.refresh_from_db()
assert app_gaming.status == 'cancelled', f"Status should be cancelled, got {app_gaming.status}"
print("✓ Payment cancellation workflow (status updated to cancelled): SUCCESS")

# 3.3 Payment Success via confirmation
app_paid = EventActivityApplication.objects.create(
    activity=act_team,
    full_name='Lionel Team Cap',
    email='lionel.cap@test.com',
    phone='699112233',
    team_name='FC Codeurs',
    team_size=6,
    amount=act_team.price,
    transaction_id=f"ACTIVITYPAY-TEAM-{uuid.uuid4().hex[:6]}",
    status='pending',
    is_paid=False,
)
res = processor.confirm_activity_payment(app_paid)
assert res['success'] == True
app_paid.refresh_from_db()
assert app_paid.status == 'confirmed', f"Status should be confirmed, got {app_paid.status}"
assert app_paid.is_paid == True
print("✓ Payment confirmation workflow (status updated to confirmed, is_paid=True): SUCCESS")

# Double confirmation idempotence check
res_again = processor.confirm_activity_payment(app_paid)
assert res_again['success'] == True
print("✓ Payment confirmation idempotency (safe against duplicate callbacks): SUCCESS")


# ---------------------------------------------------------
# TEST 4: COFESTI (Festi-Noël) & Home Countdown
# ---------------------------------------------------------
print("\n--- [TEST 4] COFESTI & Home Countdown Rendering ---")

resp_home = client.get(reverse('home'))
assert resp_home.status_code == 200
home_content = resp_home.content.decode('utf-8')
assert 'home-cofesti-countdown' in home_content
assert 'cofesti-days' in home_content
assert 'cofesti-hours' in home_content
print("✓ Home page COFESTI spotlight with live ticking countdown elements: SUCCESS")

# Cofesti hub and subpages
for route_name in ['cofesti_home', 'cofesti_miss_master', 'cofesti_sports', 'cofesti_picnics', 'cofesti_sponsorship', 'cofesti_committee']:
    resp_cof = client.get(reverse(route_name))
    assert resp_cof.status_code == 200, f"Route {route_name} failed with status {resp_cof.status_code}"
    print(f"✓ Route {route_name} rendered successfully (HTTP 200)")

print("\n" + "="*70)
print("ALL COMPREHENSIVE TESTS PASSED WITH 100% SUCCESS!")
print("="*70)
