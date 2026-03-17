#!/usr/bin/env python
"""
Script de peuplement de la base de données avec les VRAIES données du COM.S.AS.
- Crée les superutilisateurs (comsas, patrice)
- Peuple les commissions JUIN 2026
- Peuple le Bureau Exécutif 2025-2026
- Peuple les délégués
"""
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'comsas_website.settings')

# Ajouter le répertoire du projet au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from main.models import (
    Member, JUINEdition, JUINCommission, Delegate, RequestDocument,
    Event, BlogArticle, Project, Contest, JUINActivity, JUINCompetition,
    JUINTeam, SponsorshipSession
)
from datetime import date, datetime
from django.utils import timezone

print("=" * 60)
print("  COM.S.AS — Peuplement de la base de données")
print("=" * 60)

# ═══════════════════════════════════════════════════════════
# 1. SUPERUTILISATEURS
# ═══════════════════════════════════════════════════════════
print("\n[1/5] Création des superutilisateurs...")

admins = [
    {
        'username': 'comsas',
        'email': 'comsas@facsciences-uy1.cm',
        'password': 'admin@comsas',
        'first_name': 'COM.S.AS',
        'last_name': 'Admin',
    },
    {
        'username': 'patrice',
        'email': 'patrice.neussi@facsciences-uy1.cm',
        'password': 'npeprod237',
        'first_name': 'Patrice Eugène',
        'last_name': 'NEUSSI NJIETCHEU',
    },
]

for data in admins:
    user, created = User.objects.get_or_create(
        username=data['username'],
        defaults={
            'email': data['email'],
            'first_name': data['first_name'],
            'last_name': data['last_name'],
            'is_staff': True,
            'is_superuser': True,
        }
    )
    if created:
        user.set_password(data['password'])
        user.save()
        print(f"   Superutilisateur '{data['username']}' créé")
    else:
        print(f"  ℹ  Superutilisateur '{data['username']}' existe déjà")


# ═══════════════════════════════════════════════════════════
# 2. ÉDITION JUIN 2026 + COMMISSIONS
# ═══════════════════════════════════════════════════════════
print("\n[2/5] Configuration de l'édition J.U.IN 2026 et des commissions...")

edition, _ = JUINEdition.objects.get_or_create(
    edition_number=20,
    defaults={
        'title': 'Jubilé d\'Émeraude',
        'theme': 'Intelligence Artificielle et Transformation Numérique en Afrique',
        'slogan': 'Coder • Innover • Entreprendre',
        'description': (
            'La 20ème édition des Journées Universitaires de l\'Informatique (J.U.IN) '
            'marque le Jubilé d\'Émeraude du COM.S.AS. Cet événement phare réunit '
            'étudiants, chercheurs et professionnels autour de l\'innovation technologique.'
        ),
        'start_date': date(2026, 6, 1),
        'end_date': date(2026, 6, 5),
        'location': 'Campus UY1 — Faculté des Sciences',
        'is_active': True,
        'applications_open': True,
        'donations_open': True,
        'president_name': 'NEUSSI NJIETCHEU PATRICE EUGÈNE',
        'president_contact': '+237 650 970 526',
    }
)
print(f"  Édition J.U.IN 2026 (#{edition.edition_number}) prête")

# Créer les commissions si elles n'existent pas (préserve les modifications admin)
commissions_data = [
    {
        'name': 'Commission Conférences et Ateliers',
        'code': 'CA-JUIN',
        'description': (
            'Chargée de l\'organisation des conférences scientifiques, des panels de discussion '
            'et des ateliers pratiques avec les intervenants, chercheurs et professionnels du domaine informatique.'
        ),
        'icon': 'fa-microphone',
        'color': 'primary',
        'order': 1,
    },
    {
        'name': 'Commission Communication et Médiatisation',
        'code': 'CELLCOM-JUIN',
        'description': (
            'Chargée de la stratégie de communication, de la diffusion des informations relatives aux JUIN, '
            'de la gestion des réseaux sociaux, ainsi que de la médiatisation de l\'événement.'
        ),
        'icon': 'fa-bullhorn',
        'color': 'info',
        'order': 2,
    },
    {
        'name': 'Commission Infographie et Design Visuel',
        'code': 'IDV-JUIN',
        'description': (
            'Chargée de la conception graphique et de l\'identité visuelle de l\'événement : affiches, flyers, '
            'bannières, supports numériques et visuels de communication.'
        ),
        'icon': 'fa-paint-brush',
        'color': 'warning',
        'order': 3,
    },
    {
        'name': 'Commission Projets et Innovations',
        'code': 'PI-JUIN',
        'description': (
            'Chargée de la coordination des concours, expositions et présentations de projets technologiques, '
            'innovants et entrepreneuriaux réalisés par les étudiants et jeunes chercheurs.'
        ),
        'icon': 'fa-laptop-code',
        'color': 'success',
        'order': 4,
    },
    {
        'name': 'Commission Mobilisation des Ressources',
        'code': 'PMR-JUIN',
        'description': (
            'Chargée de la recherche de partenaires, sponsors et financements nécessaires '
            'à la bonne organisation des JUIN.'
        ),
        'icon': 'fa-handshake',
        'color': 'primary',
        'order': 5,
    },
    {
        'name': 'Commission Logistique et Infrastructures',
        'code': 'LOG-JUIN',
        'description': (
            'Chargée de l\'organisation matérielle de l\'événement : préparation des salles, équipements '
            'techniques, installations, gestion des espaces et coordination logistique.'
        ),
        'icon': 'fa-truck',
        'color': 'secondary',
        'order': 6,
    },
    {
        'name': 'Commission Protocole et Cérémonies',
        'code': 'PROTO-JUIN',
        'description': (
            'Chargée de l\'organisation protocolaire des cérémonies officielles (ouverture et clôture), '
            'de l\'accueil des invités et du respect des règles protocolaires.'
        ),
        'icon': 'fa-shield-alt',
        'color': 'dark',
        'order': 7,
    },
    {
        'name': 'Commission Gastronomie et Restauration',
        'code': 'GASTRO-JUIN',
        'description': (
            'Chargée de la planification et de l\'organisation de la restauration pour les participants, '
            'invités et intervenants pendant toute la durée de l\'événement.'
        ),
        'icon': 'fa-utensils',
        'color': 'danger',
        'order': 8,
    },
    {
        'name': 'Commission Animation et Divertissement',
        'code': 'ANIM-JUIN',
        'description': (
            'Chargée de l\'organisation des activités culturelles, ludiques et d\'animation destinées '
            'à dynamiser l\'événement et favoriser la convivialité.'
        ),
        'icon': 'fa-music',
        'color': 'info',
        'order': 9,
    },
    {
        'name': 'Commission Soirée de Gala',
        'code': 'GALA-JUIN',
        'description': (
            'Chargée de la préparation et de l\'organisation de la soirée de gala marquant '
            'la clôture officielle des Journées Universitaires de l\'Informatique.'
        ),
        'icon': 'fa-glass-cheers',
        'color': 'warning',
        'order': 10,
    },
]

for c in commissions_data:
    code = c.pop('code')
    comm, created = JUINCommission.objects.get_or_create(
        edition=edition, code=code, defaults=c
    )
    c['code'] = code  # Restore for print
    print(f"  {'✓' if created else 'ℹ'} {code} — {comm.name}")


# ═══════════════════════════════════════════════════════════
# 3. BUREAU EXÉCUTIF 2025-2026
# ═══════════════════════════════════════════════════════════
print("\n[3/5] Création du Bureau Exécutif 2025-2026...")

bureau_data = [
    {
        'nom_prenom': 'NEUSSI NJIETCHEU PATRICE EUGÈNE',
        'matricule': '21T2898',
        'niveau': 'M2',
        'telephone': '+237 650 970 526',
        'poste_bureau': 'Président',
        'member_type': 'bureau',
    },
    {
        'nom_prenom': 'NGUE MBONG ANDRE FITZGERALD',
        'matricule': '21T2355',
        'niveau': 'L3',
        'telephone': '+237 693 338 107',
        'poste_bureau': 'Vice-Président 1',
        'member_type': 'bureau',
    },
    {
        'nom_prenom': 'NJIFON NJOYA AROUNA FADIL',
        'matricule': '23U2348',
        'niveau': 'L3',
        'telephone': '+237 650 972 252',
        'poste_bureau': 'Vice-Président 2',
        'member_type': 'bureau',
    },
    {
        'nom_prenom': 'DJUOMBESSY DJUOMBESSY FORTUNE ANTOINETTE',
        'matricule': '23U2814',
        'niveau': 'L3',
        'telephone': '+237 654 438 809',
        'poste_bureau': 'Trésorière',
        'member_type': 'bureau',
    },
    {
        'nom_prenom': 'NISHIMWE ISABELLE',
        'matricule': '23U2765',
        'niveau': 'L3',
        'telephone': '+237 694 911 368',
        'poste_bureau': 'Secrétaire',
        'member_type': 'bureau',
    },
    {
        'nom_prenom': 'DJOMOU KOMBOU JENNIFER',
        'matricule': '25H2367',
        'niveau': 'L1',
        'telephone': '+237 657 576 210',
        'poste_bureau': 'Secrétaire Adjointe',
        'member_type': 'bureau',
    },
    {
        'nom_prenom': 'TAGNE OLA PIERRE DUREL',
        'matricule': '25G2552',
        'niveau': 'L1',
        'telephone': '+237 694 268 699',
        'poste_bureau': 'Censeur',
        'member_type': 'bureau',
    },
    {
        'nom_prenom': 'NZAPA-AKE SAMUEL',
        'matricule': '24F2544',
        'niveau': 'L2',
        'telephone': '+237 655 134 632',
        'poste_bureau': 'Censeur Adjoint',
        'member_type': 'bureau',
    },
    {
        'nom_prenom': 'EMAMBOU TCHUNKOUA ULRICH',
        'matricule': '24F2957',
        'niveau': 'L1',
        'telephone': '+237 651 359 307',
        'poste_bureau': 'Commissaire aux Comptes 1',
        'member_type': 'bureau',
    },
    {
        'nom_prenom': 'ANDOH ESSIMBI JEAN-FRANÇOIS',
        'matricule': '23V2350',
        'niveau': 'L2',
        'telephone': '+237 698 735 802',
        'poste_bureau': 'Commissaire aux Comptes 2',
        'member_type': 'bureau',
    },
    {
        'nom_prenom': 'NDJONG CEDRIC ALLAN',
        'matricule': '23V2058',
        'niveau': 'L3',
        'telephone': '+237 683 941 228',
        'poste_bureau': 'Conseiller Technique',
        'member_type': 'conseil',
    },
]

for m in bureau_data:
    member, created = Member.objects.get_or_create(
        matricule=m['matricule'],
        defaults={
            'nom_prenom': m['nom_prenom'],
            'niveau': m['niveau'],
            'telephone': m['telephone'],
            'email': f"{m['matricule'].lower()}@facsciences-uy1.cm",
            'poste_bureau': m['poste_bureau'],
            'member_type': m['member_type'],
            'is_active': True,
            'date_naissance': date(2000, 1, 1),
            'lieu_naissance': 'Yaoundé',
        }
    )
    status = "créé" if created else "existe déjà"
    print(f"  {'' if created else 'ℹ '} {m['poste_bureau']}: {m['nom_prenom']} ({status})")


# ═══════════════════════════════════════════════════════════
# 4. DÉLÉGUÉS 2025-2026
# ═══════════════════════════════════════════════════════════
print("\n[4/5] Création des délégués...")

delegates_data = [
    # Informatique - Licence 1
    {'name': 'EMAMBOU TCHUNKOUA ULRICH', 'level': 'L1', 'phone': '651359307', 'email': 'devguyuix@gmail.com'},
    {'name': 'NGO NTJEGA TECLAIRE MAROUELLE', 'level': 'L1', 'phone': '654232286', 'email': 'marouellengontjega@gmail.com'},
    {'name': 'SORAY DJOMOU KOMBOU JENNIFER', 'level': 'L1', 'phone': '657576210', 'email': 'jenniferkombou@gmail.com'},
    {'name': 'TAGNE OLA PIERRE DURREL', 'level': 'L1', 'phone': '692409817', 'email': 'pharaondurrel@gmail.com'},
    {'name': 'DJOUGOU WINNIE', 'level': 'L1', 'phone': '698563091', 'email': 'winnieange72@gmail.com'},
    {'name': 'SIEYOJI DIVINE IDES', 'level': 'L1', 'phone': '657651565', 'email': ''},
    {'name': 'FOGUE TUENO SUZANE MIREILLE', 'level': 'L1', 'phone': '', 'email': ''},
    {'name': 'DIMITRY NGUNGE MANYANGI', 'level': 'L1', 'phone': '671727930', 'email': 'dimitryngunge5@gmail.com'},

    # Informatique - Licence 2
    {'name': 'KEMGOU WAFACK SAMIRA', 'level': 'L2', 'phone': '682595643', 'email': 'kemgousamira10@gmail.com'},
    {'name': 'KUEMATSA TALACFO HYACINTHE', 'level': 'L2', 'phone': '670621549', 'email': 'kuematsahy@gmail.com'},
    {'name': 'MOAKO EKANGO BILL ARMEL', 'level': 'L2', 'phone': '657496928', 'email': 'armel.moako@facsciences-uy1.cm'},
    {'name': 'NYUMEA PEHA DARYL GERVAIS', 'level': 'L2', 'phone': '657987954', 'email': 'gervais.nyumea@facsciences-uy1.cm'},
    {'name': 'SAMY JACQUES LAFLEUR EBETE', 'level': 'L2', 'phone': '658461659', 'email': 'ebete.samy@facsciences-uy1.cm'},
    {'name': 'EYAMO SONG ANANGA MARIE DANIELLA', 'level': 'L2', 'phone': '659425964', 'email': 'daniellasong06@gmail.com'},

    # Informatique - Licence 3
    {'name': 'DJUOMBESSY DJUOMBESSY FORTUNE ANTOINETTE', 'level': 'L3', 'phone': '654438809', 'email': ''},
    {'name': "SI'BEFON NOUAYE DEBORA VICTOIRE", 'level': 'L3', 'phone': '', 'email': ''},
    {'name': 'NDJONG CEDRIC ALLAN', 'level': 'L3', 'phone': '683941228', 'email': ''},
    {'name': 'NAJELA MELVIS NURVI', 'level': 'L3', 'phone': '', 'email': ''},
    {'name': 'FONAYEN CHRISTIAN', 'level': 'L3', 'phone': '681144815', 'email': 'asangwa.fonayen23@facsciences-uy1.cm'},
    {'name': 'ETONDE MABONGO ULRICH EDOUARD', 'level': 'L3', 'phone': '', 'email': 'edouard.etonde@facsciences-uy1.cm'},

]

count_new = 0
count_exist = 0
for d in delegates_data:
    _, created = Delegate.objects.get_or_create(
        name=d['name'], year='2025-2026',
        defaults={
            'level': d['level'],
            'phone': d.get('phone', ''),
            'email': d.get('email', ''),
        }
    )
    if created:
        count_new += 1
    else:
        count_exist += 1

print(f"   {count_new} délégués créés, {count_exist} existants")


# ═══════════════════════════════════════════════════════════
# 5. MODÈLES DE REQUÊTES (Word + PDF)
# ═══════════════════════════════════════════════════════════
print("\n[5/5] Création des modèles de requêtes...")

requests_data = [
    {
        'num': 1,
        'title': 'Demande de publication de note (CC/SN/Session)',
        'description': (
            'Modèle de requête adressé au Responsable de l\'UE pour demander '
            'la publication d\'une note de Contrôle Continu, Session Normale ou Session de rattrapage. '
            'À utiliser lorsque vos notes ne sont pas encore affichées après le délai normal.'
        ),
    },
    {
        'num': 2,
        'title': 'Demande de rectification de matricule',
        'description': (
            'Modèle de requête pour signaler et demander la correction d\'un matricule erroné '
            'dans le système universitaire. Joindre les pièces justificatives (acte de naissance, '
            'carte d\'étudiant, reçu de paiement).'
        ),
    },
    {
        'num': 3,
        'title': 'Demande de blocage temporaire de matricule',
        'description': (
            'Modèle de requête adressé au Vice-Doyen chargé de la scolarité pour demander '
            'le blocage temporaire d\'un matricule. Utile en cas de vol, perte ou utilisation '
            'frauduleuse de votre matricule.'
        ),
    },
    {
        'num': 4,
        'title': 'Demande d\'activation de matricule',
        'description': (
            'Modèle de requête adressé au Vice-Doyen chargé de la scolarité pour demander '
            'l\'activation ou la réactivation d\'un matricule bloqué ou inactif.'
        ),
    },
    {
        'num': 5,
        'title': 'Demande de changement de filière',
        'description': (
            'Modèle de requête adressé au Doyen de la Faculté pour solliciter un changement '
            'de filière. Indiquer la filière actuelle et la filière souhaitée avec justification.'
        ),
    },
    {
        'num': 6,
        'title': 'Guide de retrait de documents à la scolarité',
        'description': (
            'Document détaillant la composition du dossier nécessaire pour le retrait du certificat '
            'de scolarité et autres documents administratifs. Contient les pièces à fournir pour '
            'les niveaux Licence (L1-L3), Master (M1) et les cas particuliers.'
        ),
    },
    {
        'num': 7,
        'title': 'Demande de consultation de copies d\'examen',
        'description': (
            'Modèle de requête adressé au Chef de Département pour demander la consultation '
            'de copies d\'examen. À utiliser pour vérifier vos notes ou comprendre votre évaluation.'
        ),
    },
    {
        'num': 8,
        'title': 'Demande de transfert universitaire',
        'description': (
            'Modèle de requête adressé au Doyen de la Faculté pour demander un transfert '
            'vers une autre université. Préciser l\'université de destination et le motif du transfert.'
        ),
    },
    {
        'num': 9,
        'title': 'Problème d\'affectation de classe (plateforme en ligne)',
        'description': (
            'Modèle de requête adressé au Vice-Doyen pour signaler un problème d\'affectation de classe '
            'sur la plateforme d\'inscription en ligne (inscription-uy1.uninet.cm). '
            'À utiliser lorsque le message "Vous n\'êtes affecté(e) à aucune classe" s\'affiche.'
        ),
    },
    {
        'num': 10,
        'title': 'Problème de reconnaissance des droits universitaires',
        'description': (
            'Modèle de requête adressé au Vice-Doyen pour signaler un problème de reconnaissance '
            'des droits universitaires sur la plateforme. À utiliser lorsque le message '
            '"Droits universitaires introuvables" s\'affiche malgré le paiement effectué.'
        ),
    },
    {
        'num': 11,
        'title': 'Demande de rectification de nom/prénom',
        'description': (
            'Modèle de requête adressé au Responsable de l\'UE pour corriger une erreur '
            'sur votre nom ou prénom dans les listes d\'étudiants. Joindre une copie '
            'de l\'acte de naissance comme justificatif.'
        ),
    },
    {
        'num': 12,
        'title': 'Demande de rectification d\'une note erronée',
        'description': (
            'Modèle de requête adressé au Responsable de l\'UE pour signaler et demander '
            'la correction d\'une erreur sur une note d\'examen. Préciser la note affichée, '
            'la note attendue et l\'explication probable de l\'erreur.'
        ),
    },
    {
        'num': 13,
        'title': 'Demande de rattrapage de Contrôle Continu',
        'description': (
            'Modèle de requête adressé au Responsable de l\'UE pour demander l\'autorisation '
            'de rattraper un Contrôle Continu manqué. Joindre obligatoirement un justificatif '
            'd\'absence (certificat médical, convocation officielle, etc.).'
        ),
    },
]

req_count = 0
for r in requests_data:
    num = r['num']
    # Créer la version Word si elle n'existe pas
    RequestDocument.objects.get_or_create(
        title=f"{r['title']} (Word)",
        defaults={
            'description': r['description'],
            'file': f"requests/documents/{num}.docx",
            'doc_type': 'word',
        }
    )
    # Créer la version PDF si elle n'existe pas
    RequestDocument.objects.get_or_create(
        title=f"{r['title']} (PDF)",
        defaults={
            'description': r['description'],
            'file': f"requests/documents/{num}.pdf",
            'doc_type': 'pdf',
        }
    )
    req_count += 1
    print(f"  📄 {r['title']} (Word + PDF)")

print(f"   {req_count} modèles créés ({req_count * 2} fichiers)")


# ═══════════════════════════════════════════════════════════
# 6. ÉVÉNEMENTS / ACTIVITÉS DU COM.S.AS
# ═══════════════════════════════════════════════════════════
print("\n[6/11] Création des événements...")

events_data = [
    {
        'title_fr': 'Séminaire de Maintenance Informatique',
        'title_en': 'Computer Maintenance Seminar',
        'image': 'events/event_maintenance.png',
        'description_fr': (
            '<p>Le <strong>Séminaire de Maintenance Informatique</strong> organisé par le COM.S.AS a rassemblé '
            'plus de <strong>90 participants</strong> durant <strong>2 jours intensifs</strong>.</p>'
            '<p>Au programme :</p>'
            '<ul>'
            '<li>Diagnostic matériel et logiciel (pannes courantes PC et laptops)</li>'
            '<li>Nettoyage interne, remplacement de composants (RAM, SSD, écrans)</li>'
            '<li>Installation et configuration d\'OS (Windows, Linux)</li>'
            '<li>Réseaux : câblage, sertissage RJ45, configuration Wi-Fi</li>'
            '<li>Travaux pratiques sur machines réelles</li>'
            '</ul>'
            '<p>Ce séminaire a confirmé l\'engagement du COM.S.AS dans la formation pratique des étudiants.</p>'
        ),
        'description_en': (
            '<p>The <strong>Computer Maintenance Seminar</strong> organized by COM.S.AS brought together '
            'over <strong>90 participants</strong> over <strong>2 intensive days</strong>.</p>'
            '<p>Topics covered hardware/software diagnostics, component replacement, OS installation, '
            'and network cabling with hands-on practice.</p>'
        ),
        'date_event': timezone.make_aware(datetime(2025, 11, 15, 8, 0)),
        'location': 'Salle TP Informatique — Faculté des Sciences, UY1',
        'max_participants': 100,
        'registration_deadline': timezone.make_aware(datetime(2025, 11, 14, 23, 59)),
        'is_featured': True,
        'is_active': False,  # Déjà passé
        'certificate_enabled': True,
        'certificate_title': 'Attestation de participation — Séminaire Maintenance Informatique',
        'certificate_president_name': 'NEUSSI NJIETCHEU Patrice Eugène',
        'certificate_president_title': 'Président du COM.S.AS',
    },
    {
        'title_fr': 'Session de Parrainage 2026',
        'title_en': 'Mentorship Session 2026',
        'description_fr': (
            '<p>Le <strong>Programme de Parrainage</strong> du COM.S.AS connecte les étudiants seniors '
            '(L3, M1, M2) avec les nouveaux étudiants (L1, L2) pour un accompagnement académique et professionnel.</p>'
            '<p><strong>Avantages pour les filleuls :</strong></p>'
            '<ul>'
            '<li>Conseils personnalisés sur les choix de filière et d\'UE</li>'
            '<li>Aide à la compréhension des cours et méthodes de travail</li>'
            '<li>Accès à un réseau d\'entraide entre promotions</li>'
            '<li>Préparation aux examens et partage de ressources</li>'
            '</ul>'
            '<p>Les inscriptions sont ouvertes du <strong>17 mars au 25 avril 2026</strong>.</p>'
        ),
        'description_en': (
            '<p>The COM.S.AS <strong>Mentorship Program</strong> connects senior students '
            'with newcomers for academic and professional guidance.</p>'
        ),
        'date_event': timezone.make_aware(datetime(2026, 4, 1, 9, 0)),
        'location': 'Campus UY1 — Faculté des Sciences',
        'max_participants': 200,
        'registration_deadline': timezone.make_aware(datetime(2026, 4, 25, 23, 59)),
        'is_featured': True,
        'is_active': True,
    },
    {
        'title_fr': 'Séminaire DevOps & Outils IA',
        'title_en': 'DevOps & AI Tools Seminar',
        'image': 'events/event_devops.png',
        'description_fr': (
            '<p>Le COM.S.AS organise un <strong>séminaire intensif</strong> dédié aux '
            '<strong>pratiques DevOps</strong> et aux <strong>outils d\'Intelligence Artificielle</strong>.</p>'
            '<p><strong>Programme prévu :</strong></p>'
            '<ul>'
            '<li><strong>DevOps :</strong> CI/CD avec GitHub Actions, Docker, déploiement automatisé</li>'
            '<li><strong>IA pratique :</strong> ChatGPT, GitHub Copilot, Gemini — comment les utiliser efficacement</li>'
            '<li><strong>Cloud :</strong> Introduction à AWS/GCP, hébergement de projets</li>'
            '<li><strong>Atelier :</strong> Créer et déployer une application complète en 2h</li>'
            '</ul>'
            '<p>Ouvert à tous les étudiants de la Faculté des Sciences.</p>'
        ),
        'description_en': (
            '<p>An intensive seminar on <strong>DevOps practices</strong> and <strong>AI tools</strong>, '
            'covering CI/CD, Docker, ChatGPT, GitHub Copilot, and cloud deployment.</p>'
        ),
        'date_event': timezone.make_aware(datetime(2026, 4, 28, 9, 0)),
        'location': 'Amphithéâtre 700 — Faculté des Sciences, UY1',
        'max_participants': 150,
        'registration_deadline': timezone.make_aware(datetime(2026, 4, 27, 23, 59)),
        'is_featured': True,
        'is_active': True,
        'certificate_enabled': True,
        'certificate_title': 'Attestation — Séminaire DevOps & IA',
        'certificate_president_name': 'NEUSSI NJIETCHEU Patrice Eugène',
        'certificate_president_title': 'Président du COM.S.AS',
    },
]

Event.objects.all().delete()
for e in events_data:
    Event.objects.create(**e)
    print(f"  🎯 {e['title_fr']}")


# ═══════════════════════════════════════════════════════════
# 7. ACTIVITÉS J.U.IN 2026
# ═══════════════════════════════════════════════════════════
print("\n[7/11] Création des activités J.U.IN 2026...")

# Création des activités (get_or_create)
juin_activities = [
    {
        'title': 'Cérémonie d\'Ouverture — Jubilé d\'Émeraude',
        'description': (
            'Cérémonie officielle d\'ouverture de la 20ème édition des J.U.IN, '
            'marquant le Jubilé d\'Émeraude du COM.S.AS. Discours des autorités académiques, '
            'présentation du programme et lancement officiel des festivités.'
        ),
        'activity_type': 'ceremonie',
        'date_activity': timezone.make_aware(datetime(2026, 6, 1, 9, 0)),
        'location': 'Amphithéâtre 700 — UY1',
        'speaker': 'Doyen de la Faculté des Sciences, Président du COM.S.AS',
        'is_featured': True,
        'order': 1,
    },
    {
        'title': 'Conférence : IA et Transformation Numérique en Afrique',
        'description': (
            'Conférence inaugurale sur le thème central de cette édition. '
            'Des experts du domaine présenteront les avancées de l\'intelligence artificielle '
            'et leur impact sur le continent africain, avec un focus sur les opportunités '
            'pour les jeunes développeurs camerounais.'
        ),
        'activity_type': 'conference',
        'date_activity': timezone.make_aware(datetime(2026, 6, 1, 11, 0)),
        'location': 'Amphithéâtre 700 — UY1',
        'speaker': 'Invités spéciaux (Industrie & Recherche)',
        'is_featured': True,
        'order': 2,
    },
    {
        'title': 'Ligue des Informaticiens — Football ⚽',
        'description': (
            'Le tournoi de football inter-niveaux du département ! '
            'Chaque niveau (L1, L2, L3, M1, M2, ICT-L1, ICT-L2, ICT-L3) présente une équipe de 15 joueurs. '
            'Les niveaux à grand effectif peuvent inscrire 2 équipes. '
            'Matchs en format mini-championnat puis élimination directe. '
            'Trophée du Jubilé d\'Émeraude pour l\'équipe championne !'
        ),
        'activity_type': 'sport',
        'date_activity': timezone.make_aware(datetime(2026, 6, 2, 14, 0)),
        'location': 'Terrain de Sport — Campus UY1',
        'is_featured': True,
        'order': 3,
    },
    {
        'title': 'Ligue des Informaticiens — Basketball 🏀',
        'description': (
            'Le tournoi de basketball inter-niveaux ! '
            'Chaque niveau constitue une équipe de 12 joueurs. '
            'Format de compétition : poules puis phases finales. '
            'Un moment de sport, de fair-play et de cohésion entre les promotions.'
        ),
        'activity_type': 'sport',
        'date_activity': timezone.make_aware(datetime(2026, 6, 3, 14, 0)),
        'location': 'Terrain de Basketball — Campus UY1',
        'is_featured': True,
        'order': 4,
    },
    {
        'title': 'Exposition de Projets Étudiants',
        'description': (
            'Les étudiants présentent leurs projets innovants devant un jury '
            'composé de professeurs et de professionnels. Applications mobiles, '
            'systèmes embarqués, solutions web, IA appliquée — '
            'le meilleur de la créativité informatique du département.'
        ),
        'activity_type': 'exposition',
        'date_activity': timezone.make_aware(datetime(2026, 6, 3, 9, 0)),
        'location': 'Hall d\'exposition — Faculté des Sciences',
        'is_featured': True,
        'order': 5,
    },
    {
        'title': 'Atelier : Développement Mobile avec Flutter',
        'description': (
            'Atelier pratique de 3h pour apprendre les bases du développement '
            'mobile cross-platform avec Flutter et Dart. Les participants repartiront '
            'avec une application fonctionnelle sur leur téléphone.'
        ),
        'activity_type': 'atelier',
        'date_activity': timezone.make_aware(datetime(2026, 6, 2, 9, 0)),
        'location': 'Salle TP Informatique — UY1',
        'speaker': 'Formateurs COM.S.AS',
        'order': 6,
    },
    {
        'title': 'Concours de Pitch Entrepreneurial',
        'description': (
            'Les équipes disposent de 5 minutes pour pitcher leur projet tech '
            'devant un jury d\'entrepreneurs et d\'investisseurs. '
            'Prix pour les 3 meilleures présentations.'
        ),
        'activity_type': 'pitch',
        'date_activity': timezone.make_aware(datetime(2026, 6, 4, 10, 0)),
        'location': 'Amphithéâtre 700 — UY1',
        'order': 7,
    },
    {
        'title': 'Soirée de Gala — Jubilé d\'Émeraude 🎉',
        'description': (
            'La soirée de clôture exceptionnelle de cette 20ème édition. '
            'Remise des prix, performances artistiques, cocktail dînatoire '
            'et célébration des 20 ans d\'histoire du COM.S.AS. '
            'Dress code : Élégance et Émeraude.'
        ),
        'activity_type': 'gala',
        'date_activity': timezone.make_aware(datetime(2026, 6, 5, 19, 0)),
        'location': 'Salle des Fêtes — Campus UY1',
        'is_featured': True,
        'order': 8,
    },
    {
        'title': 'Cérémonie de Clôture et Remise des Prix',
        'description': (
            'Cérémonie officielle de clôture avec remise des trophées et attestations. '
            'Meilleur développeur, meilleur projet, Miss & Master, meilleur délégué — '
            'tous les lauréats seront honorés.'
        ),
        'activity_type': 'ceremonie',
        'date_activity': timezone.make_aware(datetime(2026, 6, 5, 15, 0)),
        'location': 'Amphithéâtre 700 — UY1',
        'order': 9,
    },
]

JUINActivity.objects.filter(edition=edition).delete()
for a in juin_activities:
    JUINActivity.objects.create(edition=edition, **a)
    print(f"  📅 {a['title']}")


# ═══════════════════════════════════════════════════════════
# 8. COMPÉTITIONS J.U.IN 2026
# ═══════════════════════════════════════════════════════════
print("\n[8/11] Création des compétitions J.U.IN 2026...")

# Création des compétitions (get_or_create)
competitions_data = [
    {
        'name': 'Ligue des Informaticiens — Football',
        'comp_type': 'sport',
        'description': (
            'Le grand tournoi de football inter-niveaux du Département d\'Informatique ! '
            'Chaque niveau (L1, L2, L3, M1, M2, ICT-L1, ICT-L2, ICT-L3) compose une équipe de 15 joueurs. '
            'Les niveaux à grand effectif (L1, L2) peuvent inscrire jusqu\'à 2 équipes. '
            'Format : Phase de poules → Quarts de finale → Demi-finales → Grande Finale. '
            'Le trophée du Jubilé d\'Émeraude attend les champions !'
        ),
        'rules': (
            '• Équipes de 15 joueurs (11 titulaires + 4 remplaçants)\n'
            '• Niveaux : L1, L2, L3, M1, M2, ICT-L1, ICT-L2, ICT-L3\n'
            '• Les niveaux à +100 étudiants peuvent inscrire 2 équipes (ex: L1-A, L1-B)\n'
            '• Matchs de 2x20 minutes\n'
            '• Carte d\'étudiant obligatoire pour chaque joueur\n'
            '• Fair-play exigé — tout comportement antisportif = exclusion'
        ),
        'max_teams': 12,
        'is_open': True,
        'start_date': timezone.make_aware(datetime(2026, 6, 2, 14, 0)),
    },
    {
        'name': 'Ligue des Informaticiens — Basketball',
        'comp_type': 'sport',
        'description': (
            'Le tournoi de basketball inter-niveaux ! '
            'Chaque niveau forme une équipe de 12 joueurs (5 titulaires + 7 remplaçants). '
            'Un vrai spectacle de sport et de cohésion entre les promotions.'
        ),
        'rules': (
            '• Équipes de 12 joueurs (5 titulaires + 7 remplaçants)\n'
            '• Niveaux : L1, L2, L3, M1, M2, ICT-L1, ICT-L2, ICT-L3\n'
            '• Matchs de 4x8 minutes\n'
            '• Carte d\'étudiant obligatoire pour chaque joueur\n'
            '• Arbitrage officiel fourni par le COM.S.AS'
        ),
        'max_teams': 10,
        'is_open': True,
        'start_date': timezone.make_aware(datetime(2026, 6, 3, 14, 0)),
    },
    {
        'name': 'Meilleur Développeur du Département',
        'comp_type': 'computer',
        'description': (
            'Le concours phare pour les passionnés de code ! '
            'Les candidats affrontent des défis de programmation en temps réel : '
            'algorithmes, structures de données, développement web et résolution de problèmes. '
            'Le gagnant reçoit le titre prestigieux de Meilleur Développeur du Département '
            'et un lot de prix offerts par les partenaires.'
        ),
        'rules': (
            '• Individuel ou en binôme\n'
            '• 3 épreuves : Algorithmique (1h), Développement Web (1h30), Challenge Final (45min)\n'
            '• Langages autorisés : Python, JavaScript, Java, C/C++, PHP\n'
            '• Accès Internet interdit pendant les épreuves\n'
            '• Étudiants inscrits au département d\'informatique uniquement'
        ),
        'max_teams': 30,
        'is_open': True,
        'start_date': timezone.make_aware(datetime(2026, 6, 3, 9, 0)),
    },
    {
        'name': 'Meilleur Projet Impactant',
        'comp_type': 'computer',
        'description': (
            'Ce concours récompense le projet étudiant ayant le plus fort impact social, '
            'technologique ou environnemental. Les équipes présentent leurs projets devant '
            'un jury de professeurs et de professionnels. '
            'Critères : Innovation, Faisabilité, Impact, Qualité technique.'
        ),
        'rules': (
            '• Équipes de 2 à 5 membres\n'
            '• Projet doit avoir un prototype fonctionnel\n'
            '• Présentation de 10 minutes + 5 minutes de Q&A\n'
            '• Documentation technique requise\n'
            '• Le projet doit répondre à un besoin réel identifié'
        ),
        'max_teams': 20,
        'is_open': True,
        'start_date': timezone.make_aware(datetime(2026, 6, 4, 10, 0)),
    },
]

JUINCompetition.objects.filter(edition=edition).delete()
for c in competitions_data:
    JUINCompetition.objects.create(edition=edition, **c)
    print(f"  🏆 {c['name']}")


# ═══════════════════════════════════════════════════════════
# 9. CONCOURS (Miss & Master, Meilleur Délégué)
# ═══════════════════════════════════════════════════════════
print("\n[9/11] Création des concours...")

# Création des concours (get_or_create)
contests_data = [
    {
        'title': 'Miss & Master du Département d\'Informatique 2026',
        'slug': 'miss-master-info-2026',
        'image': 'contests/contest_missmaster.png',
        'description': (
            'Le grand concours d\'élégance, d\'éloquence et de culture générale du département ! '
            'Les candidat(e)s de chaque niveau s\'affrontent à travers des épreuves de '
            'présentation, culture générale informatique, talent artistique et tenue de soirée. '
            'Le public vote en ligne pour ses favoris. Qui succédera au trône ?'
        ),
        'start_date': timezone.make_aware(datetime(2026, 6, 1, 0, 0)),
        'end_date': timezone.make_aware(datetime(2026, 6, 5, 23, 59)),
        'is_active': True,
        'allow_public_candidates': True,
    },
    {
        'title': 'Meilleur Délégué du Département 2025-2026',
        'slug': 'meilleur-delegue-2026',
        'image': 'contests/contest_delegate.png',
        'description': (
            'Ce prix honore le délégué qui s\'est le plus démarqué au cours de l\'année académique '
            '2025-2026 par son engagement, son leadership, sa disponibilité et son impact positif '
            'sur sa promotion. Les étudiants votent pour élire le meilleur représentant de classe.'
        ),
        'start_date': timezone.make_aware(datetime(2026, 6, 1, 0, 0)),
        'end_date': timezone.make_aware(datetime(2026, 6, 4, 23, 59)),
        'is_active': True,
        'allow_public_candidates': False,
    },
]

Contest.objects.all().delete()
for c in contests_data:
    Contest.objects.create(**c)
    title = c.get('title', c.get('slug'))
    print(f"  👑 {title}")


# ═══════════════════════════════════════════════════════════
# 10. SESSION DE PARRAINAGE 2026
# ═══════════════════════════════════════════════════════════
print("\n[10/11] Création de la session de parrainage 2026...")

# Création (get_or_create)
session, _ = SponsorshipSession.objects.get_or_create(
    name='Session de Parrainage 2026 — Semestre 2',
    defaults={
        'start_date': date(2026, 3, 17),
        'end_date': date(2026, 4, 25),
        'is_active': True,
    }
)
print(f"   {session.name} (du {session.start_date} au {session.end_date})")


# ═══════════════════════════════════════════════════════════
# 11. BLOG + PROJETS
# ═══════════════════════════════════════════════════════════
print("\n[11/11] Création des articles de blog et projets...")

# --- Blog Articles (get_or_create) ---
# Récupérer un auteur
author = Member.objects.filter(matricule='21T2898').first()  # Président

blog_articles = [
    {
        'title': 'Comment réussir sa première année en Informatique à l\'UY1 : Guide Complet',
        'slug': 'reussir-premiere-annee-informatique-uy1',
        'image': 'blog/blog_l1_guide.png',
        'category': 'conseil',
        'is_published': True,
        'views_count': 342,
        'likes_count': 87,
        'content': (
            '<h2>🎓 Bienvenue dans le monde de l\'informatique !</h2>'
            '<p>Tu viens d\'être admis en <strong>Licence 1 Informatique</strong> à la Faculté des Sciences '
            'de l\'Université de Yaoundé I ? Félicitations ! Mais attention, la L1 est une année charnière '
            'qui détermine souvent tout le reste de ton parcours. Voici nos conseils pour la réussir brillamment.</p>'

            '<h3> 1. Comprendre le système LMD</h3>'
            '<p>Le système Licence-Master-Doctorat (LMD) fonctionne avec des <strong>Unités d\'Enseignement (UE)</strong> '
            'et des <strong>crédits</strong>. Tu dois valider un minimum de 30 crédits par semestre pour avancer normalement.</p>'
            '<ul>'
            '<li><strong>CC (Contrôle Continu) :</strong> 30% de ta note finale — ne le néglige JAMAIS</li>'
            '<li><strong>SN (Session Normale) :</strong> 70% — c\'est l\'examen de fin de semestre</li>'
            '<li><strong>Rattrapage :</strong> ta seconde chance si tu échoues en SN</li>'
            '</ul>'

            '<h3> 2. Les UE incontournables de L1</h3>'
            '<p>Certaines UE sont là pour te construire :</p>'
            '<ul>'
            '<li><strong>Algorithmique :</strong> La base de tout. Maîtrise les boucles, les conditions, les tableaux.</li>'
            '<li><strong>Programmation C :</strong> Ton premier vrai langage. Code chaque jour, même 30 minutes.</li>'
            '<li><strong>Mathématiques discrètes :</strong> Logique, ensembles, relations — essentiel pour l\'informatique théorique.</li>'
            '<li><strong>Architecture des ordinateurs :</strong> Comprendre comment fonctionne ta machine.</li>'
            '</ul>'

            '<h3> 3. Les outils indispensables</h3>'
            '<p>Installe ces outils dès maintenant sur ton PC :</p>'
            '<ul>'
            '<li><strong>VS Code</strong> — l\'éditeur de code le plus populaire</li>'
            '<li><strong>Git & GitHub</strong> — pour versionner tes projets</li>'
            '<li><strong>Python</strong> — le langage le plus demandé en 2026</li>'
            '<li><strong>Linux (Ubuntu)</strong> — apprends à utiliser le terminal</li>'
            '</ul>'

            '<h3> 4. Rejoins le COM.S.AS !</h3>'
            '<p>Le <strong>Comité Scientifique des Apprenants en Sciences</strong> organise des séminaires, '
            'hackathons et programmes de parrainage qui t\'aideront énormément. '
            'Ne reste pas isolé — la force du groupe est ta meilleure alliée.</p>'

            '<h3> 5. Méthode de travail gagnante</h3>'
            '<ul>'
            '<li> Révise tes cours <strong>le jour même</strong> — pas la veille de l\'examen</li>'
            '<li> Crée un <strong>groupe d\'étude</strong> de 3-4 personnes</li>'
            '<li> <strong>Code tous les jours</strong> — la programmation s\'apprend par la pratique</li>'
            '<li> Fais les <strong>anciennes épreuves</strong> — demande aux aînés</li>'
            '<li> Ne sèche pas les cours — la présence fait 50% du travail</li>'
            '</ul>'

            '<p><em>Courage et bienvenue dans la grande famille des informaticiens de l\'UY1 ! 🚀</em></p>'
        ),
    },
    {
        'title': '5 Projets GitHub qui impressionneront n\'importe quel recruteur',
        'slug': '5-projets-github-impressionner-recruteurs',
        'image': 'blog/blog_github.png',
        'category': 'stage',
        'is_published': True,
        'views_count': 518,
        'likes_count': 145,
        'content': (
            '<h2> Ton profil GitHub est ton meilleur CV</h2>'
            '<p>En 2026, les recruteurs tech regardent ton <strong>GitHub avant ton CV</strong>. '
            'Un bon portefeuille de projets vaut mieux que 100 diplômes. '
            'Voici 5 types de projets qui feront la différence.</p>'

            '<h3>1.  Une application web full-stack</h3>'
            '<p>Construis une app complète avec <strong>Django/React</strong> ou <strong>Node.js/Next.js</strong>. '
            'Par exemple : un système de gestion d\'événements, une plateforme e-learning, '
            'ou un tableau de bord analytique.</p>'
            '<p><strong>Ce que ça démontre :</strong> Maîtrise du front-end, back-end, bases de données, et déploiement.</p>'

            '<h3>2.  Une application mobile</h3>'
            '<p>Développe une app avec <strong>Flutter</strong> ou <strong>React Native</strong>. '
            'Idées : tracker de dépenses personnelles, app de révision avec flashcards, '
            'ou une app de covoiturage campus.</p>'
            '<p><strong>Ce que ça démontre :</strong> Capacité à créer des produits utilisables au quotidien.</p>'

            '<h3>3.  Un projet d\'IA/Machine Learning</h3>'
            '<p>Utilise <strong>Python + scikit-learn/TensorFlow</strong> pour résoudre un problème réel : '
            'prédiction de résultats académiques, détection de spam, '
            'ou analyse de sentiments sur les réseaux sociaux camerounais.</p>'
            '<p><strong>Ce que ça démontre :</strong> Maîtrise de la data science et de la résolution de problèmes.</p>'

            '<h3>4.  Un outil CLI ou une librairie open-source</h3>'
            '<p>Crée un outil en ligne de commande utile : gestionnaire de tâches, '
            'générateur de mots de passe sécurisés, ou un outil d\'automatisation '
            'pour les étudiants (calcul de MGP, vérification de crédits).</p>'
            '<p><strong>Ce que ça démontre :</strong> Pensée systémique et capacité à résoudre des problèmes pratiques.</p>'

            '<h3>5.  Un jeu vidéo ou une simulation</h3>'
            '<p>Développe un petit jeu avec <strong>Pygame</strong>, <strong>Unity</strong> ou en <strong>JavaScript</strong>. '
            'Les projets ludiques montrent ta créativité et ta capacité à gérer la complexité.</p>'

            '<h3> Conseils bonus</h3>'
            '<ul>'
            '<li> Chaque projet doit avoir un <strong>README.md détaillé</strong> (description, screenshots, installation)</li>'
            '<li> Fais des <strong>commits réguliers</strong> avec des messages clairs</li>'
            '<li> Utilise des <strong>branches</strong> pour montrer que tu connais Git Flow</li>'
            '<li> <strong>Déploie au moins un projet</strong> en ligne (Vercel, Railway, Heroku)</li>'
            '<li> <strong>Contribue à l\'open source</strong> — même corriger une typo compte !</li>'
            '</ul>'

            '<p><em>Commence dès aujourd\'hui. Dans 6 mois, ton GitHub sera ton passeport pour l\'emploi. 💼</em></p>'
        ),
    },
    {
        'title': 'Les J.U.IN fêtent leurs 20 ans : Retour sur deux décennies d\'innovation',
        'slug': 'juin-20-ans-jubile-emeraude-histoire',
        'image': 'blog/blog_juin20.png',
        'category': 'vie',
        'is_published': True,
        'views_count': 267,
        'likes_count': 93,
        'content': (
            '<h2> Le Jubilé d\'Émeraude — 20 éditions de passion</h2>'
            '<p>En 2026, les <strong>Journées Universitaires de l\'Informatique (J.U.IN)</strong> '
            'célèbrent leur <strong>20ème édition</strong>. Un moment historique pour le COM.S.AS '
            'et pour tout le département d\'informatique de l\'Université de Yaoundé I.</p>'

            '<h3> Les origines</h3>'
            '<p>Tout a commencé au début des années 2000, quand une poignée d\'étudiants passionnés '
            'a décidé de créer un événement pour montrer au monde que l\'informatique camerounaise '
            'avait du talent. Le premier J.U.IN fut modeste : quelques présentations de projets '
            'dans une petite salle de la Faculté des Sciences.</p>'

            '<h3> L\'évolution au fil des éditions</h3>'
            '<p>Au fil des années, les J.U.IN se sont transformés en un véritable festival tech :</p>'
            '<ul>'
            '<li><strong>2006-2010 :</strong> Les premières compétitions de programmation et expositions</li>'
            '<li><strong>2011-2015 :</strong> L\'ajout des conférences avec des professionnels de l\'industrie</li>'
            '<li><strong>2016-2020 :</strong> L\'explosion — hackathons, ligues sportives, soirées de gala</li>'
            '<li><strong>2021-2025 :</strong> La digitalisation — inscriptions en ligne, streaming, votations numériques</li>'
            '<li><strong>2026 :</strong> Le Jubilé d\'Émeraude — l\'édition la plus ambitieuse jamais organisée</li>'
            '</ul>'

            '<h3> Ce qui rend les J.U.IN uniques</h3>'
            '<p>Contrairement à un simple événement académique, les J.U.IN rassemblent :</p>'
            '<ul>'
            '<li> <strong>Ligues sportives</strong> inter-niveaux (Football & Basketball)</li>'
            '<li> <strong>Concours techniques</strong> (Meilleur Développeur, Meilleur Projet)</li>'
            '<li> <strong>Concours culturels</strong> (Miss & Master, Meilleur Délégué)</li>'
            '<li> <strong>Conférences et ateliers</strong> avec des experts nationaux et internationaux</li>'
            '<li> <strong>Soirée de Gala</strong> légendaire pour clôturer en beauté</li>'
            '</ul>'

            '<h3> Le COM.S.AS : le moteur derrière les J.U.IN</h3>'
            '<p>Chaque édition est portée par des dizaines de bénévoles organisés en '
            '<strong>10 commissions</strong> : Communication, Logistique, Conférences, '
            'Design, Projets, Protocole, Gastronomie, Animation, Gala, et Mobilisation des Ressources.</p>'

            '<p>Pour cette 20ème édition, sous le leadership du président '
            '<strong>NEUSSI NJIETCHEU Patrice Eugène</strong>, l\'ambition est claire : '
            'faire du Jubilé d\'Émeraude l\'édition dont tout le monde se souviendra.</p>'

            '<h3> Thème 2026 : "Intelligence Artificielle et Transformation Numérique en Afrique"</h3>'
            '<p>L\'IA redéfinit notre monde. Cette édition explorera comment les jeunes '
            'informaticiens africains peuvent tirer parti de cette révolution technologique '
            'pour créer des solutions adaptées aux réalités du continent.</p>'

            '<p><em>Rendez-vous du 1er au 5 juin 2026 sur le Campus UY1 ! '
            'Inscrivez-vous dès maintenant sur <strong>comsas-uy1.com/juin</strong>. </em></p>'
        ),
    },
]

BlogArticle.objects.all().delete()
for a in blog_articles:
    BlogArticle.objects.create(author=author, published_at=timezone.now(), **a)
    print(f"  📝 {a['title']}")

# --- Projets (get_or_create) ---
projects_data = [
    {
        'title_fr': 'Site Internet Officiel du COM.S.AS',
        'title_en': 'COM.S.AS Official Website',
        'description_fr': (
            '<p>Conception et développement du <strong>site internet officiel</strong> du Comité '
            'Scientifique des Apprenants en Sciences (COM.S.AS). Une plateforme complète comprenant :</p>'
            '<ul>'
            '<li>Présentation de l\'association et du bureau exécutif</li>'
            '<li>Gestion des événements, inscriptions et attestations</li>'
            '<li>Système de parrainage en ligne (parrains / filleuls)</li>'
            '<li>Portail J.U.IN avec compétitions, commissions et votes</li>'
            '<li>Blog avec articles et tutoriels pour les étudiants</li>'
            '<li>Espace requêtes avec modèles de documents téléchargeables</li>'
            '<li>Interface d\'administration complète et personnalisée</li>'
            '</ul>'
            '<p><strong>Technologies :</strong> Django, PostgreSQL, Docker, Apache, GitHub Actions CI/CD</p>'
        ),
        'description_en': (
            '<p>Design and development of the official COM.S.AS website — a comprehensive platform '
            'for the Computer Science Students\' Association at UY1.</p>'
        ),
        'status': 'completed',
        'image': 'projects/comsas_website.png',
        'budget_required': 500000,
        'budget_collected': 500000,
        'start_date': date(2025, 10, 1),
        'end_date': date(2026, 3, 15),
        'is_featured': True,
    },
    {
        'title_fr': 'Application Mobile de Suivi Académique — "MyUY1"',
        'title_en': 'Academic Tracking Mobile App — "MyUY1"',
        'description_fr': (
            '<p>Projet ambitieux de développement d\'une <strong>application mobile</strong> permettant '
            'à chaque étudiant de la Faculté des Sciences de suivre l\'intégralité de sa vie académique :</p>'
            '<ul>'
            '<li> <strong>Suivi des notes :</strong> Visualisation en temps réel des notes de CC, SN et rattrapage</li>'
            '<li> <strong>Calcul automatique du MGP :</strong> Moyenne Générale Pondérée calculée par semestre et cumulative</li>'
            '<li> <strong>Emploi du temps :</strong> Planning des cours, TD et TP synchronisé</li>'
            '<li> <strong>Gestion des UE :</strong> Liste des UE inscrites, crédits restants, progression</li>'
            '<li> <strong>Notifications :</strong> Alertes examens, publications de notes, événements COM.S.AS</li>'
            '<li> <strong>Vie associative :</strong> Accès aux événements, parrainage, et ressources du COM.S.AS</li>'
            '</ul>'
            '<p><strong>Technologies envisagées :</strong> Flutter (cross-platform), Firebase, API Django REST</p>'
            '<p><strong>Objectif :</strong> Lancer la version bêta lors du J.U.IN 2026 (Jubilé d\'Émeraude)</p>'
        ),
        'description_en': (
            '<p>An ambitious mobile app project to help every student track their academic life: '
            'grades, GPA calculation, schedules, and association activities.</p>'
        ),
        'status': 'planning',
        'image': 'projects/myuy1_app.png',
        'budget_required': 750000,
        'budget_collected': 150000,
        'start_date': date(2026, 3, 1),
        'end_date': date(2026, 9, 30),
        'is_featured': True,
    },
]

Project.objects.all().delete()
for p in projects_data:
    Project.objects.create(**p)
    print(f"  🔨 {p['title_fr']}")


# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("   Peuplement terminé avec succès !")
print("=" * 60)
print(f"""
 Résumé :
  • Superutilisateurs  : {User.objects.filter(is_superuser=True).count()}
  • Membres du Bureau  : {Member.objects.filter(member_type='bureau').count()}
  • Commissions JUIN   : {JUINCommission.objects.filter(edition=edition).count()}
  • Délégués           : {Delegate.objects.filter(year='2025-2026').count()}
  • Modèles Requêtes   : {RequestDocument.objects.count()}
  • Événements         : {Event.objects.count()}
  • Activités JUIN     : {JUINActivity.objects.filter(edition=edition).count()}
  • Compétitions JUIN  : {JUINCompetition.objects.filter(edition=edition).count()}
  • Concours           : {Contest.objects.count()}
  • Articles de Blog   : {BlogArticle.objects.count()}
  • Projets            : {Project.objects.count()}
  • Session Parrainage : {SponsorshipSession.objects.filter(is_active=True).count()}

 Accès Admin :
  • comsas / admin@comsas
  • patrice / npeprod237
""")
